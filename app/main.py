from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.routes.gralFunctions import router as GeneralFunctions_router
from app.routes.user import router as Usuario_router
from app.routes.structure import router as Structure_router
from app.routes.comparation import router as Comparation_router

# --- Lifespan event handler ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("App arrancó con la configuración CORS")
    yield
    print("App finalizando...")

app = FastAPI(lifespan=lifespan)

# --- Configuración de CORS ---
origins = [
    "http://localhost:5173",
    "http://10.0.10.157:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Rutas ---
app.include_router(GeneralFunctions_router)
app.include_router(Usuario_router)
app.include_router(Structure_router)
app.include_router(Comparation_router)

@app.get("/")
def root():
    return {"Status": "ALIVE"}
