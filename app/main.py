# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import auth, cv, benefits, admin

app = FastAPI()

# Domínio exato do frontend Vite
origins = [
    "http://jpzex.ddns.net",
]

# Inserindo CORS antes de incluir as rotas
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro das rotas - deixando prefix apenas em auth
app.include_router(auth.router, prefix="/auth")
app.include_router(cv.router, prefix="/cv")
app.include_router(benefits.router, prefix="/benefits")
app.include_router(admin.router, prefix="/admin")

@app.get("/")
def read_root():
    return {"message": "API do Portal de Apoio Social funcionando."}
