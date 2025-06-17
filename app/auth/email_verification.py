import secrets
import time
from fastapi import APIRouter, HTTPException
from pydantic import EmailStr
from app.utils.email_sender import send_verification_email

router = APIRouter()

codes = {}

class EmailPayload(BaseModel):
    email: EmailStr
    name: str

@router.post("/send-code")
def send_code(data: EmailPayload):
    code = secrets.token_hex(3)
    expires_at = time.time() + 900  # 15 minutos
    codes[data.email] = {"code": code, "expires": expires_at, "attempts": 0}
    send_verification_email(data.email, code)
    return {"message": "Código enviado com sucesso"}

@router.post("/verify-code")
def verify_code(email: EmailStr, code: str):
    if email not in codes:
        raise HTTPException(status_code=400, detail="Código não encontrado")
    entry = codes[email]
    if time.time() > entry["expires"]:
        raise HTTPException(status_code=400, detail="Código expirado")
    if entry["attempts"] >= 3:
        raise HTTPException(status_code=403, detail="Muitas tentativas erradas")
    if code != entry["code"]:
        codes[email]["attempts"] += 1
        raise HTTPException(status_code=401, detail="Código inválido")
    del codes[email]
    return {"message": "Código verificado com sucesso"}
