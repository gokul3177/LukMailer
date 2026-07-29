"""
backend/logger.py — Centralized logger with file output & real-time streaming broadcaster.
"""

import asyncio
import logging
import time
from datetime import datetime
from pathlib import Path

class LogBroadcaster:
    """
    In-memory async message broadcaster for real-time streaming to the UI.
    """
    def __init__(self):
        self.listeners: set[asyncio.Queue] = set()

    def subscribe(self) -> asyncio.Queue:
        q = asyncio.Queue()
        self.listeners.add(q)
        return q

    def unsubscribe(self, q: asyncio.Queue):
        self.listeners.discard(q)

    def publish(self, event_data: dict):
        """Broadcast a message dictionary to all active UI subscribers."""
        dead_queues = set()
        for q in self.listeners:
            try:
                q.put_nowait(event_data)
            except Exception:
                dead_queues.add(q)
        for q in dead_queues:
            self.listeners.discard(q)

broadcaster = LogBroadcaster()

class SSEHandler(logging.Handler):
    """Logging handler that broadcasts formatted logs to SSE/WebSocket subscribers."""
    def emit(self, record: logging.LogRecord):
        try:
            log_entry = {
                "timestamp": datetime.fromtimestamp(record.created).strftime("%H:%M:%S"),
                "level": record.levelname,
                "message": record.getMessage(),
                "type": getattr(record, "event_type", "log"),
                "data": getattr(record, "event_data", {}),
            }
            broadcaster.publish(log_entry)
        except Exception:
            self.handleError(record)

def setup_logger(log_file_path: str | Path = "send_log.txt") -> logging.Logger:
    logger = logging.getLogger("LukMailer")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    # Formatter
    formatter = logging.Formatter("%(asctime)s  %(levelname)-8s  %(message)s", datefmt="%H:%M:%S")

    # Console Handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # File Handler
    try:
        fh = logging.FileHandler(log_file_path, encoding="utf-8")
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    except Exception as e:
        print(f"Warning: Could not setup file logger at {log_file_path}: {e}")

    # SSE / Live UI Handler
    sse_handler = SSEHandler()
    logger.addHandler(sse_handler)

    return logger

log = setup_logger()
