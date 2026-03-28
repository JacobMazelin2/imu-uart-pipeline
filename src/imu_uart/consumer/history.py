from collections import deque

class History:

    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self._entries = deque(maxlen=max_size)

    def append(self, entry:dict):
        self._entries.append(entry)

    def get_latest(self, limit: int | None = None) -> list[dict]:
        items = list(self._entries)
        if limit is not None:
            return items[-limit:]
        return items