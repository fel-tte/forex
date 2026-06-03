from __future__ import annotations

from app.core.models import Order, OrderStatus, RobotState


class SweepAgent:
    def detect_orphans(self, state: RobotState, broker_orders: list[Order]) -> list[Order]:
        return [o for o in broker_orders if o.magic_number != state.magic_number or o.robot_id != state.robot_id]

    def sweep(self, orphans: list[Order]) -> list[Order]:
        for order in orphans:
            if order.status in {OrderStatus.OPEN, OrderStatus.PENDING}:
                order.status = OrderStatus.CANCELLED
        return orphans
