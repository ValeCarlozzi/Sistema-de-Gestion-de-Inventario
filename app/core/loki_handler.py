import logging
import json
from datetime import datetime
from typing import Optional
import requests
from queue import Queue, Full
from threading import Thread, Event


class LokiHandler(logging.Handler):
    """Handler para enviar logs a Grafana Loki"""

    def __init__(
        self,
        loki_url: str = "http://localhost:3100",
        labels: Optional[dict] = None,
        queue_size: int = 100,
    ):
        super().__init__()
        self.loki_url = loki_url.rstrip("/")
        self.labels = labels or {"app": "inventory"}
        self.queue = Queue(maxsize=queue_size)
        self.stop_event = Event()
        
        # Thread worker para enviar logs de forma asincrónica
        self.worker_thread = Thread(target=self._worker, daemon=True)
        self.worker_thread.start()

    def emit(self, record: logging.LogRecord) -> None:
        try:
            # Formatea el mensaje como JSON
            log_entry = {
                "timestamp": int(record.created * 1e9),  # Nanoseconds para Loki
                "message": self.format(record),
                "level": record.levelname,
                "logger": record.name,
            }
            self.queue.put_nowait(log_entry)
        except Full:
            pass

    def _worker(self) -> None:
        while not self.stop_event.is_set():
            try:
                log_entry = self.queue.get(timeout=1)
                self._send_to_loki(log_entry)
            except Exception:
                continue

    def _send_to_loki(self, log_entry: dict) -> None:
        try:
            # Payload de Loki (formato Protobuf JSON)
            payload = {
                "streams": [
                    {
                        "stream": self.labels,
                        "values": [
                            [
                                str(log_entry["timestamp"]),
                                log_entry["message"],
                            ]
                        ],
                    }
                ]
            }
            
            requests.post(
                f"{self.loki_url}/loki/api/v1/push",
                json=payload,
                timeout=5,
            )
        except Exception:
            pass

    def close(self) -> None:
        """Cierra el handler y el worker thread"""
        self.stop_event.set()
        super().close()
