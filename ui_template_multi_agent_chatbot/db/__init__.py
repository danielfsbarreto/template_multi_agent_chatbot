import sqlite3
import uuid
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "chatbot.db")


def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = _get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS channels (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            conversation_id TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id TEXT NOT NULL REFERENCES channels(id),
            role TEXT NOT NULL,
            content TEXT NOT NULL DEFAULT '',
            event_type TEXT,
            image_base64 TEXT,
            timestamp TEXT DEFAULT (datetime('now')),
            event_id TEXT UNIQUE
        );

        CREATE INDEX IF NOT EXISTS idx_messages_channel
            ON messages(channel_id, timestamp);

        CREATE INDEX IF NOT EXISTS idx_channels_conversation
            ON channels(conversation_id);
    """)
    conn.close()


def create_channel(name):
    channel_id = str(uuid.uuid4())
    conversation_id = str(uuid.uuid4())
    conn = _get_conn()
    conn.execute(
        "INSERT INTO channels (id, name, conversation_id) VALUES (?, ?, ?)",
        (channel_id, name, conversation_id),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM channels WHERE id = ?", (channel_id,)).fetchone()
    conn.close()
    return dict(row)


def get_channels():
    conn = _get_conn()
    rows = conn.execute("""
        SELECT c.*,
               m.content AS last_message,
               m.timestamp AS last_message_at
        FROM channels c
        LEFT JOIN (
            SELECT channel_id, content, timestamp,
                   ROW_NUMBER() OVER (PARTITION BY channel_id ORDER BY id DESC) AS rn
            FROM messages
            WHERE event_type IS NULL OR event_type = 'message_created'
        ) m ON m.channel_id = c.id AND m.rn = 1
        ORDER BY c.created_at ASC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_channel(channel_id):
    conn = _get_conn()
    row = conn.execute("SELECT * FROM channels WHERE id = ?", (channel_id,)).fetchone()
    if not row:
        conn.close()
        return None
    channel = dict(row)
    messages = conn.execute(
        "SELECT * FROM messages WHERE channel_id = ? ORDER BY id ASC",
        (channel_id,),
    ).fetchall()
    conn.close()
    channel["messages"] = [dict(m) for m in messages]
    return channel


def get_channel_by_conversation_id(conversation_id):
    conn = _get_conn()
    row = conn.execute(
        "SELECT * FROM channels WHERE conversation_id = ?",
        (conversation_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def add_message(channel_id, role, content="", event_type=None, image_base64=None, event_id=None):
    conn = _get_conn()
    try:
        conn.execute(
            """INSERT OR IGNORE INTO messages
               (channel_id, role, content, event_type, image_base64, event_id)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (channel_id, role, content, event_type, image_base64, event_id),
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM messages WHERE channel_id = ? ORDER BY id DESC LIMIT 1",
            (channel_id,),
        ).fetchone()
        conn.close()
        return dict(row) if row else None
    except Exception:
        conn.close()
        raise


def get_messages(channel_id):
    conn = _get_conn()
    rows = conn.execute(
        "SELECT * FROM messages WHERE channel_id = ? ORDER BY id ASC",
        (channel_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_channel(channel_id):
    conn = _get_conn()
    conn.execute("DELETE FROM messages WHERE channel_id = ?", (channel_id,))
    conn.execute("DELETE FROM channels WHERE id = ?", (channel_id,))
    conn.commit()
    conn.close()
