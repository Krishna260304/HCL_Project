"""
API Security Module for LearnPath AI AI/ML Service.
Enforces internal service-to-service Bearer authentication between Django and AI Service.
"""

from typing import Optional
from fastapi import Header, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.core.config import get_settings
from app.core.exceptions import AuthenticationError

security_scheme = HTTPBearer(auto_error=False)


async def verify_api_key(
    auth_header: Optional[HTTPAuthorizationCredentials] = Security(security_scheme),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> bool:
    """
    Validate that incoming requests originate from authenticated callers (e.g. Django backend).
    Accepts standard 'Authorization: Bearer <key>' or 'X-API-Key: <key>'.
    """
    settings = get_settings()
    expected_key = settings.AI_SERVICE_API_KEY

    # Check Bearer token
    token = None
    if auth_header and auth_header.credentials:
        token = auth_header.credentials
    elif x_api_key:
        token = x_api_key

    if not token or token != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error": {
                    "code": "UNAUTHORIZED",
                    "message": "Invalid or missing internal AI Service API key.",
                    "details": {},
                },
            },
        )
    return True
