import os
from fastapi import Request, HTTPException
from jose import JWTError, jwt
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET", "tomato-secret")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


def create_token(user_id: str, role: str = "user") -> str:
    """Create a JWT token for a user."""
    payload = {"user_id": str(user_id), "role": role}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        return None


async def get_current_user(request: Request) -> Optional[dict]:
    """Extract user data from cookie. Returns None if not authenticated."""
    token = request.cookies.get("access_token")
    if not token:
        return None
    return decode_token(token)


async def require_auth(request: Request) -> dict:
    """Require authenticated user. Raises 401 if not authenticated."""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


async def require_admin(request: Request) -> dict:
    """Require admin user. Raises 403 if not admin."""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
