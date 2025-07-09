# app/routes/auth.py

from fastapi import APIRouter, HTTPException, Query, Body, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from jose import jwt
import time, random, os

from app.utils.db import get_social_db
from app.models import Users, EmailCodes
from app.utils.email_sender import send_verification_email

router = APIRouter()
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"
# app/auth.py

from fastapi import APIRouter, HTTPException, Query, Body, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
import time, random, jwt, os, traceback

from app.utils.db import get_social_db
from app.models import Users, EmailCodes
from app.utils.email_sender import send_verification_email

router = APIRouter(prefix="/auth")

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"

class EmailPayload(BaseModel):
    name: str
    username: str
    email: EmailStr
    password: str

class LoginData(BaseModel):
    email: EmailStr
    password: str

@router.post("/send-code")
def send_code(data: EmailPayload, db: Session = Depends(get_social_db)):
    try:
        if db.query(Users).filter_by(username=data.username).first():
            raise HTTPException(409, detail="Nome de usuário já em uso")

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
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao enviar email: {str(e)}")

@router.post("/verify-code")
def verify_code(code: str = Query(...), data: EmailPayload = Body(...), db: Session = Depends(get_social_db)):
    try:
        rec = db.query(EmailCodes).filter_by(email=data.email).first()
        if not rec or time.time() > rec.expires:
            raise HTTPException(400, detail="Código expirado ou inválido")
        if rec.attempts >= 3:
            raise HTTPException(403, detail="Muitas tentativas incorretas")
        if rec.code != code:
            rec.attempts += 1
            db.commit()
            raise HTTPException(401, detail="Código incorreto")

        temp = rec.temp_data
        user = Users(name=temp["name"], username=temp["username"], email=data.email)
        user.set_password(temp["password"])
        db.add(user)
        db.delete(rec)
        db.commit()

        token = jwt.encode({"sub": user.id, "is_admin": user.is_admin, "exp": time.time() + 3600}, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return {"message": "Conta criada com sucesso", "token": token}
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro no registro: {str(e)}")

@router.post("/login")
def login_user(data: LoginData, db: Session = Depends(get_social_db)):
    try:
        user = db.query(Users).filter_by(email=data.email).first()
        if not user or not user.check_password(data.password):
            raise HTTPException(400, detail="Credenciais inválidas")

        token = jwt.encode({"sub": user.id, "is_admin": user.is_admin, "exp": time.time() + 3600}, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return {
            "message": "Login bem‑sucedido",
            "token": token,
            "user": {"name": user.name, "username": user.username, "email": user.email, "is_admin": user.is_admin}
        }
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro no login: {str(e)}")
