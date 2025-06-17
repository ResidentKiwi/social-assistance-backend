from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
import time
import secrets
from app.utils.email_sender import send_verification_email
from app.utils.db import supabase

router = APIRouter()

class EmailPayload(BaseModel):
    email: EmailStr
    name: str

@router.post("/send-code")
def send_code(data: EmailPayload):
    code = secrets.token_hex(3)
    expires = int(time.time()) + 900
    supabase.table("email_codes").upsert({"email": data.email, "code": code, "expires": expires, "attempts": 0}).execute()
    send_verification_email(data.email, code)
    return {"message": "Código enviado"}

@router.post("/verify-code")
def verify_code(data: EmailPayload, code: str):
    resp = supabase.table("email_codes").select("*").eq("email", data.email).single().execute()
    record = resp.data
    if not record or int(time.time()) > record["expires"]:
        raise HTTPException(status_code=400, detail="Código inválido ou expirado")
    if record["attempts"] >= 3:
        raise HTTPException(status_code=403, detail="Muitas tentativas")
    if code != record["code"]:
        supabase.table("email_codes").update({"attempts": record["attempts"] + 1}).eq("email", data.email).execute()
        raise HTTPException(status_code=401, detail="Código incorreto")
    supabase.table("email_codes").delete().eq("email", data.email).execute()
    return {"message": "Verificado com sucesso"}
