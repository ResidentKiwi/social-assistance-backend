from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, EmailStr
import time, random
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
    # Verifica se nome de usuário já existe
    existing = supabase.table("profiles").select("username").eq("username", data.username).execute()
    if existing.data:
        raise HTTPException(status_code=409, detail="Nome de usuário já em uso")

    # Gera código numérico de 6 dígitos
    code = f"{random.randint(100000, 999999)}"
    expires = int(time.time()) + 900  # expira em 15 minutos

    # Salva o código e os dados temporários no Supabase
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
    # Busca o código no banco
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

    # Recupera dados temporários
    temp = record.get("temp_data") or {}

    # Criação do usuário no Supabase Auth
    creation = supabase.auth.sign_up({
        "email": data.email,
        "password": temp["password"],
        "options": {
            "data": {
                "name": temp["name"],
                "username": temp["username"]
            }
        }
    })

    # ❗ Correção: testando erro corretamente
    if not creation.user:
        raise HTTPException(status_code=500, detail="Erro ao criar usuário")

    # Limpa o código da tabela
    supabase.table("email_codes").delete().eq("email", data.email).execute()

    return {"message": "Conta criada com sucesso"}
