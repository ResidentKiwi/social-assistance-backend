from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from app.utils.db import supabase

router = APIRouter()

class LoginData(BaseModel):
    email: EmailStr
    name: str

@router.post("/login")
def login_user(data: LoginData):
    user = supabase.table("users").select("*").eq("email", data.email).single().execute()
    if user.data is None:
        res = supabase.table("users").insert({"email": data.email, "name": data.name}).execute()
        if res.error:
            raise HTTPException(status_code=500, detail="Erro ao criar usuário")
    return {"message": "Login bem‑sucedido", "email": data.email}
