from __future__ import annotations

from app.core.config import Settings
from app.core.models import MarketTick, RiskDecision, RobotState


class RiskGuardAgent:
    def __init__(self, settings: Settings):
        self.settings = settings

    def evaluate(self, state: RobotState, tick: MarketTick | None = None, api_latency_ms: int = 0) -> RiskDecision:
        reasons: list[str] = []
        action = "ALLOW"
        if state.drawdown_pct >= self.settings.max_drawdown_pct:
            reasons.append(f"drawdown {state.drawdown_pct:.2f}% >= max {self.settings.max_drawdown_pct:.2f}%")
            action = "FREEZE"
        if state.equity <= state.balance * (1 - self.settings.equity_guard_pct / 100):
            reasons.append("equity guard threshold breached")
            action = "CLOSE_RISKY_ORDERS"
        if state.margin_level_pct < self.settings.min_margin_level_pct:
            reasons.append("margin level below minimum")
            action = "REDUCE_EXPOSURE"
        if state.consecutive_loss >= self.settings.max_consecutive_loss:
            reasons.append("consecutive loss limit reached")
            action = "COOLDOWN"
        if tick is not None:
            spread_points = tick.spread / self.settings.tick_size
            if spread_points > self.settings.max_spread_points:
                reasons.append(f"spread {spread_points:.1f} points > max {self.settings.max_spread_points:.1f}")
                action = "PAUSE_NEW_ENTRY"
        if api_latency_ms > self.settings.max_api_latency_ms:
            reasons.append("api latency too high")
            action = "PAUSE_EXECUTION"
        return RiskDecision(allowed=len(reasons) == 0, action=action, reasons=reasons)
