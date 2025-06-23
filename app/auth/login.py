from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
import time, jwt, os
from app.utils.db import get_social_db
from app.models import Users

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"

router = APIRouter()

class LoginData(BaseModel):
    email: EmailStr
    password: str

@router.post("/login")
def login_user(data: LoginData, db=Depends(get_social_db)):
    user = db.query(Users).filter_by(email=data.email).first()
    if not user or not user.check_password(data.password):
        raise HTTPException(400, "Credenciais inválidas")

    token = jwt.encode({"sub": user.id, "exp": time.time() + 3600}, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return {"message": "Login bem‑sucedido", "token": token, "user": {"name": user.name, "username": user.username, "email": user.email, "is_admin": user.is_admin}}
