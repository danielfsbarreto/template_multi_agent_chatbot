import json
import logging
import os
import queue
import threading

import db
import requests as http_requests
from dotenv import load_dotenv
from flask import Flask, Response, jsonify, render_template, request

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)

dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path)

DEPLOYMENT_URL = os.environ["DEPLOYMENT_URL"]
DEPLOYMENT_KEY = os.environ["DEPLOYMENT_KEY"]

app = Flask(__name__)
db.init_db()


@app.after_request
def _add_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    return response


@app.route("/api/webhook", methods=["OPTIONS"])
def webhook_preflight():
    return "", 204


_sse_subscribers: dict[str, list[queue.Queue]] = {}
_sse_lock = threading.Lock()


def _broadcast_to_channel(channel_id: str, event_data: dict):
    with _sse_lock:
        subscribers = _sse_subscribers.get(channel_id, [])
        for q in subscribers:
            q.put(event_data)


def _crewai_headers():
    return {
        "Authorization": f"Bearer {DEPLOYMENT_KEY}",
        "Content-Type": "application/json",
    }


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------


@app.route("/")
def index():
    return render_template("index.html")


# ---------------------------------------------------------------------------
# Channel API
# ---------------------------------------------------------------------------


@app.route("/api/channels", methods=["GET"])
def list_channels():
    return jsonify(db.get_channels())


@app.route("/api/channels", methods=["POST"])
def create_channel():
    data = request.get_json(force=True)
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "name is required"}), 400
    channel = db.create_channel(name)
    return jsonify(channel), 201


@app.route("/api/channels/<channel_id>", methods=["GET"])
def get_channel(channel_id):
    channel = db.get_channel(channel_id)
    if not channel:
        return jsonify({"error": "not found"}), 404
    return jsonify(channel)


@app.route("/api/channels/<channel_id>", methods=["DELETE"])
def delete_channel(channel_id):
    db.delete_channel(channel_id)
    return "", 204


# ---------------------------------------------------------------------------
# Messages / Kickoff
# ---------------------------------------------------------------------------


@app.route("/api/channels/<channel_id>/messages", methods=["POST"])
def send_message(channel_id):
    channel = db.get_channel(channel_id)
    if not channel:
        return jsonify({"error": "channel not found"}), 404

    data = request.get_json(force=True)
    content = data.get("content", "").strip()
    if not content:
        return jsonify({"error": "content is required"}), 400

    msg = db.add_message(channel_id, role="user", content=content)
    _broadcast_to_channel(
        channel_id,
        {
            "type": "message_created",
            "message": msg,
        },
    )

    kickoff_body = {
        "inputs": {
            "id": channel["conversation_id"],
            "user_message": {"role": "user", "content": content},
        },
    }

    app.logger.info("Kickoff body: %s", json.dumps(kickoff_body, default=str))
    app.logger.info(
        "Kickoff → id=%s content=%s",
        channel["conversation_id"],
        content[:80],
    )

    def _do_kickoff():
        try:
            resp = http_requests.post(
                f"{DEPLOYMENT_URL}/kickoff",
                headers=_crewai_headers(),
                json=kickoff_body,
                timeout=30,
            )
            if not resp.ok:
                app.logger.error(
                    "Kickoff HTTP %s: %s", resp.status_code, resp.text[:500],
                )
            resp.raise_for_status()
            result = resp.json()
            app.logger.info("Kickoff OK: %s", result)
            _broadcast_to_channel(
                channel_id,
                {
                    "type": "kickoff_started",
                    "kickoff_id": result.get("kickoff_id"),
                },
            )
        except Exception as e:
            app.logger.error("Kickoff failed: %s", e)
            _broadcast_to_channel(
                channel_id,
                {
                    "type": "kickoff_error",
                    "error": str(e),
                },
            )

    threading.Thread(target=_do_kickoff, daemon=True).start()

    return jsonify({"status": "sent", "message": msg}), 202


# ---------------------------------------------------------------------------
# Status proxy
# ---------------------------------------------------------------------------


@app.route("/api/channels/<channel_id>/status/<kickoff_id>", methods=["GET"])
def get_status(channel_id, kickoff_id):
    try:
        resp = http_requests.get(
            f"{DEPLOYMENT_URL}/{kickoff_id}/status",
            headers=_crewai_headers(),
            timeout=15,
        )
        resp.raise_for_status()
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 502


# ---------------------------------------------------------------------------
# SSE
# ---------------------------------------------------------------------------


@app.route("/api/channels/<channel_id>/events", methods=["GET"])
def channel_events(channel_id):
    def stream():
        q = queue.Queue()
        with _sse_lock:
            _sse_subscribers.setdefault(channel_id, []).append(q)
        try:
            while True:
                try:
                    event = q.get(timeout=25)
                    yield f"data: {json.dumps(event, default=str)}\n\n"
                except queue.Empty:
                    yield ": heartbeat\n\n"
        except GeneratorExit:
            pass
        finally:
            with _sse_lock:
                subs = _sse_subscribers.get(channel_id, [])
                if q in subs:
                    subs.remove(q)

    return Response(
        stream(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


# ---------------------------------------------------------------------------
# Webhook receiver (from webhook.site XHR forward)
# ---------------------------------------------------------------------------


@app.route("/api/webhook", methods=["POST"])
def webhook():
    try:
        payload = request.get_json(force=True)
    except Exception:
        return "bad json", 400

    event_type = payload.get("type")
    event_id = payload.get("event_id")
    emission_sequence = payload.get("emission_sequence", 0)
    fingerprint_metadata = payload.get("fingerprint_metadata") or {}
    conversation_id = fingerprint_metadata.get("conversation_id")

    app.logger.info(
        "Webhook received: type=%s conversation_id=%s event_id=%s",
        event_type,
        conversation_id,
        event_id,
    )

    if not conversation_id:
        return jsonify({"status": "ignored", "reason": "no conversation_id"}), 200

    channel = db.get_channel_by_conversation_id(conversation_id)
    if not channel:
        app.logger.warning(
            "No channel found for conversation_id=%s",
            conversation_id,
        )
        return jsonify({"status": "ignored", "reason": "unknown conversation"}), 200

    channel_id = channel["id"]

    if event_type == "flow_finished":
        _broadcast_to_channel(
            channel_id,
            {
                "type": "flow_finished",
                "seq": emission_sequence,
            },
        )

    elif event_type == "message_created":
        result = payload.get("result", {})
        message_data = result.get("message", {})
        role = message_data.get("role", "assistant")
        content = message_data.get("content", "")
        msg = db.add_message(
            channel_id,
            role=role,
            content=content,
            event_type="message_created",
            event_id=event_id,
        )
        if msg:
            _broadcast_to_channel(
                channel_id,
                {
                    "type": "message_created",
                    "message": msg,
                    "seq": emission_sequence,
                },
            )

    elif event_type == "image_generated":
        result = payload.get("result", {})
        image_b64 = result.get("image", "")
        msg = db.add_message(
            channel_id,
            role="assistant",
            content="",
            event_type="image_generated",
            image_base64=image_b64,
            event_id=event_id,
        )
        if msg:
            _broadcast_to_channel(
                channel_id,
                {
                    "type": "image_generated",
                    "message": msg,
                    "seq": emission_sequence,
                },
            )

    return jsonify({"status": "ok"}), 200


# ---------------------------------------------------------------------------
# Boot
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5005)),
        debug=True,
        threaded=True,
    )
