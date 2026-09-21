from pathlib import Path

from fastapi import HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.app.main import app as backend_app


frontend_dist = Path("frontend/dist")
index_file = frontend_dist / "index.html"


# Remove existing backend metadata root
for route in list(backend_app.routes):
    if (
        getattr(route, "path", None) == "/"
        and getattr(route, "methods", None)
        and "GET" in route.methods
    ):
        backend_app.routes.remove(route)


assets_dir = frontend_dist / "assets"

if assets_dir.exists():
    backend_app.mount(
        "/assets",
        StaticFiles(directory=str(assets_dir)),
        name="frontend-assets",
    )


@backend_app.get("/")
async def serve_frontend():
    if not index_file.exists():
        raise HTTPException(
            status_code=503,
            detail="Frontend build unavailable",
        )

    return FileResponse(index_file)


@backend_app.get("/{full_path:path}")
async def spa_fallback(full_path: str):

    # Preserve backend endpoints
    if full_path.startswith("api/") or full_path.startswith("ws/"):
        raise HTTPException(
            status_code=404,
            detail="Not found",
        )

    requested = frontend_dist / full_path

    if requested.exists() and requested.is_file():
        return FileResponse(requested)

    if index_file.exists():
        return FileResponse(index_file)

    raise HTTPException(
        status_code=503,
        detail="Frontend build unavailable",
    )


app = backend_app