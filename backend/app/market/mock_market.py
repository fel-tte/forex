from __future__ import annotations

import random
from datetime import datetime, timezone

from app.core.models import MarketTick


class MockMarketDataAgent:
    def __init__(self, start_price: float = 1.08000, spread: float = 0.00010):
        self.price = start_price
        self.spread = spread

    def fetch_tick(self, symbol: str) -> MarketTick:
        self.price += random.uniform(-0.00035, 0.00035)
        bid = self.price - self.spread / 2
        ask = self.price + self.spread / 2
        return MarketTick(symbol=symbol, bid=round(bid, 5), ask=round(ask, 5), timestamp=datetime.now(timezone.utc))

    def validate_independent_source(self, tick: MarketTick) -> bool:
        # MVP: simulated independent feed. Real version compares broker vs paid feed.
        simulated_mid = tick.mid + random.uniform(-0.00003, 0.00003)
        return abs(simulated_mid - tick.mid) <= 0.00005
