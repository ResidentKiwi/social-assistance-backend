# app/routes/auth.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models import Users, EmailCodes
from app.utils.db import get_social_db
from app.utils.email_sender import send_verification_email
from jose import jwt
from passlib.hash import bcrypt
import random, time, os

router = APIRouter(prefix="/auth", tags=["auth"])

# Configurações do JWT
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_SECONDS = 60 * 60 * 24 * 7  # Token válido por 7 dias

# 1. Rota para envio de código por e‑mail
@router.post("/send-code")
def send_code(name: str, username: str, email: str, password: str, db: Session = Depends(get_social_db)):
    # Remove qualquer código anterior pro mesmo e-mail
    db.query(EmailCodes).filter_by(email=email).delete()
    code = f"{random.randint(100000, 999999)}"
    expires = int(time.time()) + 900  # 15 minutos

    db.add(EmailCodes(email=email, code=code, expires=expires, temp_data={
        "name": name,
        "username": username,
        "password": password
    }))
    db.commit()

    try:
        send_verification_email(email, code)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao enviar e‑mail: {e}")

    return {"message": "Código enviado com sucesso"}

# 2. Validação do código e criação do usuário
@router.post("/verify-code")
def verify_code(email: str, code: str, db: Session = Depends(get_social_db)):
    record = db.query(EmailCodes).filter_by(email=email).first()
    if not record or record.code != code or time.time() > record.expires:
        raise HTTPException(status_code=400, detail="Código inválido ou expirado")

    temp = record.temp_data or {}
    # Cria usuário
    if db.query(Users).filter_by(email=email).first():
        raise HTTPException(status_code=409, detail="Usuário já existe")
    hashed = bcrypt.hash(temp["password"])
    user = Users(name=temp["name"], username=temp["username"], email=email, password_hash=hashed)
    db.add(user)
    db.delete(record)
    db.commit()

    payload = {
        "sub": user.id,
        "is_admin": user.is_admin,
        "exp": int(time.time()) + JWT_EXPIRATION_SECONDS
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return {"token": token}

# 3. Login — valida credenciais e retorna JWT
@router.post("/login")
def login(email: str, password: str, db: Session = Depends(get_social_db)):
    user = db.query(Users).filter_by(email=email).first()
    if not user or not bcrypt.verify(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    payload = {
        "sub": user.id,
        "is_admin": user.is_admin,
        "exp": int(time.time()) + JWT_EXPIRATION_SECONDS
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return {"token": token}
