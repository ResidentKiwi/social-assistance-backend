from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from app.utils.db import supabase

router = APIRouter()

class LoginData(BaseModel):
    email: EmailStr
    name: str

@router.post("/login")
def login_user(data: LoginData):
    resp = supabase.table("users").select("email", "name", "is_admin").eq("email", data.email).single().execute()
    record = resp.data
    if record is None:
        res = supabase.table("users").insert({
            "email": data.email,
            "name": data.name
        }).execute()
        if res.error:
            raise HTTPException(status_code=500, detail="Erro ao criar usuário")
        is_admin = False
    else:
        is_admin = record.get("is_admin", False)

    return {"email": data.email, "name": data.name, "is_admin": is_admin}
