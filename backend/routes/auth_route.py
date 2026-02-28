from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from utils.auth_service import create_new_user, authenticate_user, sign_out_user

router = APIRouter()

class AuthPayload(BaseModel):
    email: EmailStr
    password: str

@router.post("/api/auth/signup")
def signup(payload: AuthPayload):
    result = create_new_user(payload.email, payload.password)
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result.get("message", "Signup failed"))
    return result

@router.post("/api/auth/signin")
def signin(payload: AuthPayload):
    result = authenticate_user(payload.email, payload.password)
    if result.get("status") == "error":
        raise HTTPException(status_code=401, detail=result.get("message", "Invalid credentials"))
    return result

@router.post("/api/auth/signout")
def signout():
    result = sign_out_user()
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result.get("message", "Signout failed"))
    return result
