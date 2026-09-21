"""
PRAHARI-NET Railway SPA wrapper.
Serves the built React dashboard and preserves FastAPI /api + /ws routes.
"""

from pathlib import Path

from fastapi import HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.app.main import app as backend_app


frontend_dist = Path("frontend/dist")
index_file = frontend_dist / "index.html"


# Remove only the existing backend metadata GET /
for route in list(backend_app.routes):
    if (
        getattr(route, "path", None) == "/"
        and getattr(route, "methods", None)
        and "GET" in route.methods
    ):
        backend_app.routes.remove(route)


# Serve Vite assets
assets_dir = frontend_dist / "assets"

if assets_dir.exists():
    backend_app.mount(
        "/assets",
        StaticFiles(directory=str(assets_dir)),
        name="frontend-assets",
    )


@backend_app.get("/")
async def frontend_root():
    if not index_file.exists():
        raise HTTPException(
            status_code=503,
            detail="Frontend build is unavailable",
        )

    return FileResponse(index_file)


@backend_app.get("/{full_path:path}")
async def frontend_spa_fallback(full_path: str):

    # Never turn unknown API endpoints into React pages
    if full_path.startswith("api/") or full_path.startswith("ws/"):
        raise HTTPException(status_code=404, detail="Not found")

    requested_file = frontend_dist / full_path

    # Serve manifest/icons/etc from Vite public output
    if requested_file.exists() and requested_file.is_file():
        return FileResponse(requested_file)

    # React Router fallback
    if index_file.exists():
        return FileResponse(index_file)

    raise HTTPException(
        status_code=503,
        detail="Frontend build is unavailable",
    )


app = backend_app