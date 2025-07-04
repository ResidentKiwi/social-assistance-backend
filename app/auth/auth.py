from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from app.models import Users, EmailCodes
from app.utils.db import get_social_db
from app.utils.email_sender import send_verification_email
from jose import jwt
import random, time, os
from passlib.hash import bcrypt

router = APIRouter(prefix="/auth", tags=["auth"])

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"

@router.post("/send-code")
def send_code(email: str, db: Session = Depends(get_social_db)):
    code = str(random.randint(100000, 999999))
    expires = int(time.time()) + 900

    db.query(EmailCodes).filter_by(email=email).delete()
    db.add(EmailCodes(email=email, code=code, expires=expires))
    db.commit()
    send_verification_email(email, code)
    return {"ok": True}

@router.post("/verify-code")
def verify_code(data: dict, db: Session = Depends(get_social_db)):
    email = data["email"]
    code = data["code"]
    record = db.query(EmailCodes).filter_by(email=email).first()
    if not record or record.code != code or time.time() > record.expires:
        raise HTTPException(400, "Código inválido ou expirado")

    user = Users(
        email=email,
        username=data["username"],
        name=data["name"],
        password_hash=bcrypt.hash(data["password"])
    )
    db.add(user)
    db.query(EmailCodes).filter_by(email=email).delete()
    db.commit()

    payload = {"sub": user.id, "is_admin": user.is_admin}
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return {"token": token}

@router.post("/login")
def login(data: dict, db: Session = Depends(get_social_db)):
    user = db.query(Users).filter_by(email=data["email"]).first()
    if not user or not bcrypt.verify(data["password"], user.password_hash):
        raise HTTPException(401, "Credenciais inválidas")

    payload = {"sub": user.id, "is_admin": user.is_admin}
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return {"token": token}
