from fastapi import Request, HTTPException, status
from jose import jwt, JWTError
from jose.backends.cryptography_backend import CryptographyECKey
import requests
from core.config import settings
import logging

logger = logging.getLogger(__name__)

if not settings.SUPABASE_URL:
    raise RuntimeError("SUPABASE_URL is not configured - Security failing")

JWKS_URL = f"{settings.SUPABASE_URL}/auth/v1/.well-known/jwks.json"

try:
    jwks = requests.get(JWKS_URL).json()
except Exception as e:
    logger.warning(f"Failed to fetch JWKS on startup: {e}")
    jwks = {"keys": []}

async def get_current_user(request: Request):
    global jwks
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authentication token"
        )

    token = auth_header.split(" ")[1]
 
    try:
        headers = jwt.get_unverified_header(token)
        kid = headers.get("kid")
        if not kid:
            raise JWTError("kid missing from headers")

        jwk_key = next((k for k in jwks.get("keys", []) if k["kid"] == kid), None)
        
        # If not found, possibly JWKS rotated, so fetch again
        if not jwk_key:
            # global jwks
            jwks = requests.get(JWKS_URL).json()
            jwk_key = next((k for k in jwks.get("keys", []) if k["kid"] == kid), None)
            if not jwk_key:
                raise JWTError("matching key not found in JWKS")

        # Convert JWK to proper EC key
        public_key = CryptographyECKey(jwk_key, algorithm="ES256")

        payload = jwt.decode(
            token,
            public_key,
            algorithms=["ES256"],
            audience="authenticated",
        )

        return payload

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )
