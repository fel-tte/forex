from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from app.core.config import Settings
from app.core.models import Order, OrderStatus


class ExecutionAdapterAgent:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.log_path = Path(settings.logs_path)

    def execute(self, order: Order) -> Order:
        if self.settings.broker_mode != "mock" and not self.settings.allow_live_execution:
            order.status = OrderStatus.REJECTED
            self._log({"event": "ORDER_REJECTED_LIVE_DISABLED", "order": order.model_dump(mode="json")})
            return order
        order.status = OrderStatus.OPEN
        order.broker_order_id = f"MOCK-{uuid4()}"
        self._log({"event": "ORDER_OPENED", "order": order.model_dump(mode="json")})
        return order

    def _log(self, payload: dict) -> None:
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, default=str) + "\n")
