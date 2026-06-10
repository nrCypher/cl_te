"""FastAPI application factory.

Wires the routers, serves the static Gantt demo, and exposes a health check.
The app holds no business logic — every endpoint delegates to a service.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api import (
    routes_analytics,
    routes_machines,
    routes_schedule,
    routes_scenarios,
    routes_solve,
    routes_work_orders,
)
from app.config import get_settings

_FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description=(
            "Modular production-scheduling prototype for a sheet-metal "
            "workshop: synthetic simulator + OR-Tools CP-SAT solver + KPIs."
        ),
    )

    # Permissive CORS so a separately served frontend can call the API.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    api_routers = [
        routes_scenarios.router,
        routes_machines.router,
        routes_work_orders.router,
        routes_solve.router,
        routes_schedule.router,
        routes_analytics.router,
    ]
    for router in api_routers:
        app.include_router(router, prefix="/api")

    @app.get("/health", tags=["meta"])
    def health() -> dict[str, str]:
        return {"status": "ok", "app": settings.app_name}

    if _FRONTEND_DIR.exists():
        app.mount(
            "/ui",
            StaticFiles(directory=str(_FRONTEND_DIR), html=True),
            name="ui",
        )

        @app.get("/", include_in_schema=False)
        def index() -> FileResponse:
            return FileResponse(str(_FRONTEND_DIR / "index.html"))

    return app


app = create_app()
