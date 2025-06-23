from fastapi import APIRouter, HTTPException, Query, Body, Depends
from pydantic import BaseModel, EmailStr
import time, secrets, random, jwt, os
from app.utils.db import get_social_db
from app.models import Users, EmailCodes  # definimos no ORM
from app.utils.email_sender import send_verification_email

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"

router = APIRouter()

class EmailPayload(BaseModel):
    name: str
    username: str
    email: EmailStr
    password: str

@router.post("/send-code")
def send_code(data: EmailPayload, db=Depends(get_social_db)):
    existing = db.query(Users).filter_by(username=data.username).first()
    if existing: raise HTTPException(409, "Nome de usuário já em uso")

    code = f"{random.randint(100000, 999999)}"
    expires = int(time.time()) + 900
    temp = {"name": data.name, "username": data.username, "password": data.password}

    entry = db.query(EmailCodes).filter_by(email=data.email).first()
    if entry:
        entry.code = code
        entry.expires = expires
        entry.attempts = 0
        entry.temp_data = temp
    else:
        db.add(EmailCodes(email=data.email, code=code, expires=expires, attempts=0, temp_data=temp))
    db.commit()

    send_verification_email(data.email, code)
    return {"message": "Código enviado"}

@router.post("/verify-code")
def verify_code(code: str = Query(...), data: EmailPayload = Body(...), db=Depends(get_social_db)):
    rec = db.query(EmailCodes).filter_by(email=data.email).first()
    if not rec or time.time() > rec.expires:
        raise HTTPException(400, "Código expirado ou inválido")
    if rec.attempts >= 3:
        raise HTTPException(403, "Muitas tentativas")
    if rec.code != code:
        rec.attempts += 1
        db.commit()
        raise HTTPException(401, "Código incorreto")

    temp = rec.temp_data
    # cria o usuário
    user = Users(name=temp["name"], username=temp["username"], email=data.email)
    user.set_password(temp["password"])
    db.add(user)
    db.delete(rec)
    db.commit()

    # criamos token JWT
    token = jwt.encode({"sub": user.id, "exp": time.time() + 3600}, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return {"message": "Conta criada", "token": token}
