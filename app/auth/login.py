from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from app.utils.db import supabase

router = APIRouter()

class LoginData(BaseModel):
    email: EmailStr
    password: str

@router.post("/login")
def login_user(data: LoginData):
    # Supabase Auth já trata as credenciais, então apenas retorna status
    user_resp = supabase.auth.sign_in_with_password({
        "email": data.email,
        "password": data.password
    })
    if "error" in user_resp:
        raise HTTPException(status_code=400, detail=user_resp["error"]["message"])
    return {"message": "Login bem‑sucedido", "user": user_resp["data"]["user"]}
