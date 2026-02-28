from config.settings import supabase, jwks_url
import requests
from jose import jwt
from jose.exceptions import JWTError
from fastapi import HTTPException, Request

_jwks = None

def _get_jwks():
    global _jwks
    if _jwks is None:
        jwks = requests.get(jwks_url, timeout=5).json()
        _jwks = jwks["keys"]
    return _jwks


def get_user_id(request: Request) -> str:
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = auth_header.replace("Bearer ", "")

    try:
        payload = jwt.decode(
            token,
            _get_jwks(),
            algorithms=["ES256"],
            audience="authenticated",
            options={"verify_exp": True},
        )
    except JWTError:
        global _jwks
        _jwks = None
        try:
            payload = jwt.decode(
                token,
                _get_jwks(),
                algorithms=["ES256"],
                audience="authenticated",
                options={"verify_exp": True},
            )
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

    return payload["sub"]


def create_new_user(email, password):
    try:
        resp = supabase.auth.sign_up({"email": email, "password": password})
        return {"status": "success", "data": resp.data}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def authenticate_user(email, password):
    try:
        resp = supabase.auth.sign_in_with_password({"email": email, "password": password})
        session = resp.get("session") if isinstance(resp, dict) else getattr(resp, "session", None)
        user = resp.get("user") if isinstance(resp, dict) else getattr(resp, "user", None)

        access_token = None
        if session:
            access_token = session.get("access_token") if isinstance(session, dict) else getattr(session, "access_token", None)

        return {
            "status": "success",
            "access_token": access_token,
            "user": user,
            "session": session,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

def sign_out_user():
    try:
        supabase.auth.sign_out()
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
