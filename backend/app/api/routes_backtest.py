from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.runtime import genes_memory, optimizer

router = APIRouter(prefix="/api/v1/backtest", tags=["backtest"])


class BacktestRequest(BaseModel):
    symbol: str = "EURUSD"
    timeframe: str = "M1"
    step_range: list[float] = [0.0005, 0.001, 0.0015]
    x_range: list[int] = [1, 2, 3]
    risk_range: list[float] = [0.25, 0.5, 1.0]


@router.post("/run")
def run_backtest(req: BacktestRequest):
    gene = optimizer.run(req.symbol, req.timeframe, req.step_range, req.x_range, req.risk_range)
    genes_memory.remember(gene)
    return {"winner_gene_set": gene}
