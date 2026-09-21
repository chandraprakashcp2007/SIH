"""
PRAHARI-NET LOCAL SIH DEMO SERVER

This wrapper adds local-development authentication bypass
without deleting or replacing the real authentication system.

Run production with backend.app.main:app instead.
"""

from fastapi import Request
from fastapi.responses import JSONResponse

from backend.app.main import app


DEMO_USER = {
    "id": 1,
    "username": "PRAHARI Developer",
    "name": "PRAHARI Developer",
    "full_name": "PRAHARI Developer",
    "email": "developer@prahari.local",
    "role": "ADMIN",
    "is_active": True,
    "permissions": ["*"]
}


@app.middleware("http")
async def prahari_sih_demo_auth(request: Request, call_next):

    path = request.url.path.rstrip("/").lower()

    # ---------------------------------------------
    # DEVELOPMENT LOGIN BYPASS
    # ---------------------------------------------

    login_paths = {
        "/api/auth/login",
        "/auth/login",
        "/api/v1/auth/login"
    }

    if request.method.upper() == "POST" and path in login_paths:

        return JSONResponse(
            status_code=200,
            content={
                "success": True,

                "access_token": "prahari-sih-demo-token",
                "token": "prahari-sih-demo-token",

                "refresh_token": "prahari-sih-demo-refresh",

                "token_type": "bearer",

                "expires_in": 86400,

                "user": DEMO_USER,

                "username": DEMO_USER["username"],

                "name": DEMO_USER["name"],

                "role": "ADMIN",

                "mode": "DEVELOPMENT",

                "dev_auth_bypass": True,

                "message": "PRAHARI-NET SIH demo authentication active"
            }
        )

    # ---------------------------------------------
    # CURRENT USER
    # ---------------------------------------------

    me_paths = {
        "/api/auth/me",
        "/auth/me",
        "/api/v1/auth/me"
    }

    if request.method.upper() == "GET" and path in me_paths:

        return JSONResponse(
            status_code=200,
            content=DEMO_USER
        )

    # ---------------------------------------------
    # EVERYTHING ELSE -> REAL PRAHARI APPLICATION
    # ---------------------------------------------

    return await call_next(request)
