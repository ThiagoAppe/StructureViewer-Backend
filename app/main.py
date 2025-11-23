from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.routes.gralFunctions import router as general_functions_router
from app.routes.user import router as usuario_router
from app.routes.structure import router as structure_router
from app.routes.comparation import router as comparation_router
from app.routes.documents import router as documents_router
from app.routes.articulos import router as articulos_router

from Backend.app.services.documents.document_handler.document_handler import StartWatchdogScheduler

# variable para guardar scheduler y poder detenerlo
scheduler = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Contexto de ciclo de vida de la aplicación.
    Inicia el watchdog scheduler al arrancar y lo detiene al finalizar.
    """
    global scheduler
    print("App arrancó con la configuración CORS")

    scheduler = StartWatchdogScheduler()

    yield

    print("App finalizando...")
    if scheduler:
        scheduler.shutdown()
        print("Scheduler detenido")


app = FastAPI(title="MERP", lifespan=lifespan)

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
app.include_router(general_functions_router)
app.include_router(usuario_router)
app.include_router(structure_router)
app.include_router(articulos_router)
app.include_router(comparation_router)
app.include_router(documents_router)


@app.get("/")
def root():
    """
    Endpoint simple para verificar el estado del servicio.
    """
    return {"Status": "ALIVE"}
