from fastapi import Request, HTTPException, status
from jose import jwt, JWTError
from jose.utils import base64url_decode
from jose.backends.cryptography_backend import CryptographyECKey
import requests
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")

if not SUPABASE_URL:
    raise RuntimeError("SUPABASE_URL is not configured")

JWKS_URL = f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json"

jwks = requests.get(JWKS_URL).json()

async def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authentication token"
        )

    token = auth_header.split(" ")[1]
 
    try:
        headers = jwt.get_unverified_header(token)
        kid = headers["kid"]

        jwk_key = next(k for k in jwks["keys"] if k["kid"] == kid)

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