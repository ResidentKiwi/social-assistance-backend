from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, EmailStr
import time, random
from app.utils.db import SessionLocal
from app.utils.email_sender import send_verification_email
from app.models import User, EmailCode, Profile
import bcrypt

router = APIRouter()

class EmailPayload(BaseModel):
    name: str
    username: str
    email: EmailStr
    password: str

@router.post("/send-code")
def send_code(data: EmailPayload):
    db = SessionLocal()
    if db.query(Profile).filter(Profile.username == data.username).first():
        raise HTTPException(status_code=409, detail="Nome de usuário já em uso")

    code = f"{random.randint(100000, 999999)}"
    expires = int(time.time()) + 900

    # insere ou atualiza
    obj = db.query(EmailCode).filter(EmailCode.email == data.email).first()
    if not obj:
        obj = EmailCode(email=data.email)
    obj.code = code
    obj.expires = expires
    obj.attempts = 0
    obj.temp_name = data.name
    obj.temp_username = data.username
    obj.temp_password_hash = bcrypt.hashpw(data.password.encode(), bcrypt.gensalt()).decode()
    db.add(obj); db.commit()

    send_verification_email(data.email, code)
    return {"message": "Código de verificação enviado."}


@router.post("/verify-code")
def verify_code(code: str = Query(...), data: EmailPayload = Body(...)):
    db = SessionLocal()
    rec = db.query(EmailCode).filter(EmailCode.email == data.email).first()
    if not rec or time.time() > rec.expires:
        raise HTTPException(status_code=400, detail="Código expirado ou inválido")
    if rec.attempts >= 3:
        raise HTTPException(status_code=403, detail="Muitas tentativas inválidas")
    if rec.code != code:
        rec.attempts += 1
        db.commit()
        raise HTTPException(status_code=401, detail="Código incorreto")

    # cria usuário
    pw = rec.temp_password_hash.encode()
    new_user = User(
        email = data.email,
        password_hash = pw,
        name = rec.temp_name,
        username = rec.temp_username
    )
    db.add(new_user); db.commit()
    db.refresh(new_user)

    # cria perfil padrão
    profile = Profile(user_id=new_user.id, is_admin=False)
    db.add(profile)

    # remove o código usado
    db.delete(rec)
    db.commit()

    return {"message": "Conta criada com sucesso"}
