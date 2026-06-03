from __future__ import annotations

from app.core.models import WinnerGene
from app.core.state_store import GeneStore


class WinnerGenesMemoryAgent:
    def __init__(self, store: GeneStore):
        self.store = store

    def remember(self, gene: WinnerGene) -> WinnerGene:
        self.store.add(gene)
        return gene

    def winners(self) -> list[WinnerGene]:
        return self.store.list()

    def promote(self, symbol: str, timeframe: str) -> WinnerGene | None:
        return self.store.promote(symbol, timeframe)
