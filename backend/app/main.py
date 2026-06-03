from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_backtest import router as backtest_router
from app.api.routes_dashboard import router as dashboard_router
from app.api.routes_fsm import router as fsm_router
from app.api.routes_genes import router as genes_router
from app.api.routes_grid import router as grid_router
from app.api.routes_guard import router as guard_router
from app.api.routes_robot import router as robot_router
from app.core.config import get_settings

settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(robot_router)
app.include_router(grid_router)
app.include_router(fsm_router)
app.include_router(guard_router)
app.include_router(backtest_router)
app.include_router(genes_router)
app.include_router(dashboard_router)


@app.get("/health")
def health():
    return {"ok": True, "app": settings.app_name, "broker_mode": settings.broker_mode, "live_enabled": settings.allow_live_execution}
