from __future__ import annotations

from datetime import datetime, timezone

from app.brain.fsm import FsmBrainAgent
from app.core.config import get_settings
from app.core.models import FsmState, RobotState, RobotStatus
from app.core.state_store import GeneStore, JsonStateStore
from app.execution.order_router import ExecutionAdapterAgent
from app.guard.risk_guard import RiskGuardAgent
from app.market.mock_market import MockMarketDataAgent
from app.memory.trading_memory import WinnerGenesMemoryAgent
from app.optimization.gene_search import BacktestOptimizationAgent
from app.strategy.hedge_engine import HedgeEngine

settings = get_settings()
state_store = JsonStateStore(settings.storage_path)
gene_store = GeneStore(settings.genes_path)
market_agent = MockMarketDataAgent()
risk_guard = RiskGuardAgent(settings)
fsm_brain = FsmBrainAgent()
hedge_engine = HedgeEngine(settings.base_lot, settings.max_exposure_lots)
execution_agent = ExecutionAdapterAgent(settings)
optimizer = BacktestOptimizationAgent()
genes_memory = WinnerGenesMemoryAgent(gene_store)


def get_or_create_robot_state() -> RobotState:
    restored = state_store.load_robot()
    if restored:
        return restored
    state = RobotState(
        robot_id=settings.robot_id,
        symbol=settings.default_symbol,
        broker=settings.broker_mode,
        magic_number=settings.magic_number,
        fsm_state=FsmState.BOOT,
    )
    state_store.save_robot(state)
    return state


def save_robot_state(state: RobotState) -> RobotState:
    state.last_heartbeat = datetime.now(timezone.utc)
    state_store.save_robot(state)
    return state
