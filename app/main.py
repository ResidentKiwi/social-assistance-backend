from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importações de rotas após declarar app
from app.auth import login, email_verification
from app.routes import cv, benefits, admin

app = FastAPI()

# CORS para frontend no GitHub Pages ou qualquer domínio
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Troque por domínio fixo se quiser mais segurança
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registra todas as rotas
app.include_router(login.router, prefix="/auth")
app.include_router(email_verification.router, prefix="/auth")
app.include_router(cv.router, prefix="/cv")
app.include_router(benefits.router, prefix="/benefits")
app.include_router(admin.router, prefix="/admin")

@app.get("/")
def read_root():
    return {"message": "API do Portal de Apoio Social funcionando."}
