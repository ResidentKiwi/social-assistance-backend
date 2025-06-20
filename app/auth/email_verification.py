from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, EmailStr
import time, secrets, random
from app.utils.db import supabase
from app.utils.email_sender import send_verification_email

router = APIRouter()

class EmailPayload(BaseModel):
    name: str
    username: str
    email: EmailStr
    password: str

@router.post("/send-code")
def send_code(data: EmailPayload):
    existing = supabase.table("profiles").select("username").eq("username", data.username).execute()
    if existing.data:
        raise HTTPException(status_code=409, detail="Nome de usuário já em uso")

    code = f"{random.randint(100000, 999999)}"
    expires = int(time.time()) + 900

    supabase.table("email_codes").upsert({
        "email": data.email,
        "code": code,
        "expires": expires,
        "attempts": 0,
        "temp_data": {
            "name": data.name,
            "username": data.username,
            "password": data.password
        }
    }).execute()

    send_verification_email(data.email, code)
    return {"message": "Código de verificação enviado."}

@router.post("/verify-code")
def verify_code(code: str = Query(...), data: EmailPayload = Body(...)):
    resp = supabase.table("email_codes").select("*").eq("email", data.email).single().execute()
    record = resp.data

    if not record or time.time() > record["expires"]:
        raise HTTPException(status_code=400, detail="Código expirado ou inválido")

    if record["attempts"] >= 3:
        raise HTTPException(status_code=403, detail="Muitas tentativas inválidas")

    if record["code"] != code:
        supabase.table("email_codes")\
            .update({"attempts": record["attempts"] + 1}).eq("email", data.email).execute()
        raise HTTPException(status_code=401, detail="Código incorreto")

    temp = record.get("temp_data") or {}

    # Criação de usuário sem envio de e-mail automático
    creation = supabase.auth.sign_up({
        "email": data.email,
        "password": temp["password"],
        "options": {
            "emailRedirectTo": None,  # Evita disparo de e-mail
            "data": {
                "name": temp["name"],
                "username": temp["username"]
            }
        }
    })

    if getattr(creation, "error", None):
        raise HTTPException(status_code=500, detail="Erro ao criar usuário")

    supabase.table("email_codes").delete().eq("email", data.email).execute()
    return {"message": "Conta criada com sucesso"}
