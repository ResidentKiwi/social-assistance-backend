from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.utils.auth_utils import admin_required
from app.utils.db import get_social_db
from app.models import Users

router = APIRouter()

@router.get("/users")
def list_users(_: bool = Depends(admin_required),
               db: Session = Depends(get_social_db)):
    users = db.query(Users).all()
    return {"users": [dict(
        id=u.id, email=u.email, name=u.name,
        is_admin=u.is_admin, created_at=u.created_at.isoformat()
    ) for u in users]}

@router.post("/users/promote")
def promote_user(email: str,
                 _: bool = Depends(admin_required),
                 db: Session = Depends(get_social_db)):
    user = db.query(Users).filter_by(email=email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    user.is_admin = True
    db.commit()
    return {"message": f"{email} promovido a admin"}

@router.post("/users/demote")
def demote_user(email: str,
                _: bool = Depends(admin_required),
                db: Session = Depends(get_social_db)):
    user = db.query(Users).filter_by(email=email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    user.is_admin = False
    db.commit()
    return {"message": f"{email} despromovido a usuário"}
