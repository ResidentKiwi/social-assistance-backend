from fastapi import APIRouter, Depends, HTTPException, Header
from app.utils.db import supabase
from app.utils.auth_utils import admin_required

router = APIRouter()

@router.get("/users")
def list_users(x_user_email: str = Header(...),
               _: bool = Depends(admin_required)):
    res = supabase.table("users").select("id, email, name, is_admin, created_at").execute()
    if res.error:
        raise HTTPException(status_code=500, detail="Erro ao listar usuários")
    return {"users": res.data}

@router.post("/users/promote")
def promote_user(email: str, x_user_email: str = Header(...),
                 _: bool = Depends(admin_required)):
    supabase.table("users").update({"is_admin": True}).eq("email", email).execute()
    return {"message": f"{email} promovido a admin"}

@router.post("/users/demote")
def demote_user(email: str, x_user_email: str = Header(...),
                _: bool = Depends(admin_required)):
    supabase.table("users").update({"is_admin": False}).eq("email", email).execute()
    return {"message": f"{email} despromovido a usuário"}
