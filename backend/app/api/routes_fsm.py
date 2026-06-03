from __future__ import annotations

from fastapi import APIRouter

from app.core.config import get_settings
from app.core.runtime import (
    execution_agent,
    fsm_brain,
    get_or_create_robot_state,
    hedge_engine,
    market_agent,
    risk_guard,
    save_robot_state,
    state_store,
)
from app.strategy.grid_math import calculate_grid

router = APIRouter(prefix="/api/v1/fsm", tags=["fsm"])
settings = get_settings()


@router.post("/tick")
def tick():
    state = get_or_create_robot_state()
    tick_data = market_agent.fetch_tick(state.symbol)
    independent_ok = market_agent.validate_independent_source(tick_data)
    risk = risk_guard.evaluate(state, tick_data)
    if not independent_ok:
        risk.allowed = False
        risk.action = "PAUSE_EXECUTION"
        risk.reasons.append("independent data source validation failed")

    cycle = state_store.load_cycle(state.current_cycle_id) if state.current_cycle_id else None
    grid = calculate_grid(state.symbol, tick_data.mid, tick_data.mid, settings.default_step_size, settings.default_x_level, settings.tick_size)
    executed = []

    if state.status == "RUNNING" and risk.allowed:
        if cycle is None:
            cycle = hedge_engine.open_base_hedge(state, tick_data)
            state.current_cycle_id = cycle.cycle_id
            for order in cycle.buy_orders + cycle.sell_orders:
                executed.append(execution_agent.execute(order))
            state_store.save_cycle(cycle)
        else:
            grid = calculate_grid(state.symbol, cycle.buy_orders[0].entry_price, tick_data.mid, settings.default_step_size, settings.default_x_level, settings.tick_size)
            surplus_orders = hedge_engine.evaluate_surplus(state, cycle, grid, tick_data)
            for order in surplus_orders:
                opened = execution_agent.execute(order)
                executed.append(opened)
                if opened.side == "BUY":
                    cycle.buy_orders.append(opened)
                else:
                    cycle.sell_orders.append(opened)
            state_store.save_cycle(cycle)

    state.fsm_state = fsm_brain.next_state(state, risk, has_cycle=cycle is not None, surplus_active=bool(executed and cycle and cycle.surplus_side != "NONE"))
    state.last_step = grid.current_step
    save_robot_state(state)
    return {"state": state, "tick": tick_data, "grid": grid, "risk": risk, "executed_orders": executed, "cycle": cycle}
