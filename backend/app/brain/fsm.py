from __future__ import annotations

from app.core.models import FsmState, RiskDecision, RobotState, RobotStatus


class FsmBrainAgent:
    def next_state(self, state: RobotState, risk: RiskDecision, has_cycle: bool, surplus_active: bool = False) -> FsmState:
        if not risk.allowed:
            if risk.action == "FREEZE":
                state.status = RobotStatus.FROZEN
                return FsmState.FREEZE
            if risk.action in {"COOLDOWN", "PAUSE_EXECUTION", "PAUSE_NEW_ENTRY"}:
                state.status = RobotStatus.COOLDOWN
                return FsmState.IDLE
        if state.status == RobotStatus.STOPPED:
            return FsmState.IDLE
        if state.fsm_state in {FsmState.BOOT, FsmState.RESTORE_STATE}:
            return FsmState.SYNC_BROKER
        if not has_cycle:
            return FsmState.BUILD_GRID
        if surplus_active:
            return FsmState.SURPLUS_ACTIVE
        return FsmState.HEDGE_ACTIVE
