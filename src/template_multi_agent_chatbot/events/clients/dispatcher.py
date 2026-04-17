import os

import requests


class Dispatcher:
    def __init__(self):
        self._url = os.environ["DISPATCHER_URL"]
        self._key = os.environ["DISPATCHER_KEY"]
        self._request_headers = {
            "Authorization": f"Bearer {self._key}",
            "Content-Type": "application/json",
        }

    def dispatch(self, event_payload: dict):
        try:
            response = requests.post(
                self._url,
                headers=self._request_headers,
                json=event_payload,
            )
            response.raise_for_status()
        except Exception as e:
            print(f"Error dispatching event to {self._url}: {e}")
            raise
