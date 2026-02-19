from fastapi import Header, HTTPException
from google.auth.transport import requests
from google.oauth2 import id_token

from app.config import settings


def get_current_user_id(authorization: str | None = Header(default=None)) -> str:
    # Development mode: allow requests without token if ALLOW_DEV_AUTH is True
    if settings.allow_dev_auth and not authorization:
        return settings.dev_user_id
    
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization token")

    token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Missing authorization token")

    try:
        audience = settings.google_client_id or None
        payload = id_token.verify_oauth2_token(token, requests.Request(), audience=audience)
    except ValueError as exc:
        # In dev mode, accept any token-like string as valid
        if settings.allow_dev_auth:
            # Extract a user_id-like value from the token or use dev user
            try:
                from jwt import decode as jwt_decode
                decoded = jwt_decode(token, options={"verify_signature": False})
                user_id = str(decoded.get("sub") or decoded.get("email") or "").strip()
                if user_id:
                    return user_id
            except Exception:
                pass
            return settings.dev_user_id
        raise HTTPException(status_code=401, detail="Invalid OAuth token") from exc

    user_id = str(payload.get("sub") or payload.get("email") or "").strip()
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid OAuth token")

    return user_id
