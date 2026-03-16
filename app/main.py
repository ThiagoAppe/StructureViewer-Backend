from ___loggin___.logger import get_logger, LogArea, LogCategory
_ = get_logger(LogArea.CORE, LogCategory.SYSTEM)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.routes.user import router as usuario_router
from app.routes.structure import router as structure_router
from app.routes.documents import router as documents_router
from app.routes.articulos import router as articulos_router

from app.services.files.files_handler import start_watchdog_scheduler

from zeroconf import Zeroconf, ServiceInfo
import socket
import threading


# -------------------------------
# Variables globales
# -------------------------------

scheduler = None
zeroconf = None
service_info = None


# -------------------------------
# Obtener IP real (no localhost)
# -------------------------------

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


# -------------------------------
# mDNS
# -------------------------------

def register_mdns(port=80):
    global zeroconf, service_info

    ip = get_local_ip()
    ip_bytes = socket.inet_aton(ip)

    zeroconf = Zeroconf()

    service_info = ServiceInfo(
        "_http._tcp.local.",
        "ingenieria._http._tcp.local.",
        addresses=[ip_bytes],
        port=port,
        properties={},
        server="ingenieria.local."
    )

    zeroconf.register_service(service_info)

    print(f"mDNS publicado: http://ingenieria.local:{port}")


def unregister_mdns():
    global zeroconf, service_info

    if zeroconf and service_info:
        zeroconf.unregister_service(service_info)
        zeroconf.close()
        print("mDNS desregistrado")


# -------------------------------
# Lifecycle
# -------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):

    global scheduler

    print("App arrancó con la configuración CORS")

    # registrar mDNS en thread
    threading.Thread(target=register_mdns, daemon=True).start()

    scheduler = start_watchdog_scheduler()

    yield

    print("App finalizando...")

    if scheduler:
        scheduler.shutdown()
        print("Scheduler detenido")

    unregister_mdns()


# -------------------------------
# App
# -------------------------------

app = FastAPI(
    title="MERP",
    lifespan=lifespan
)


# -------------------------------
# CORS
# -------------------------------

origins = [
    "http://localhost:5173",
    "http://10.0.10.157:5173",
    "http://ingenieria.local",
    "http://ingenieria.local:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------
# Routers
# -------------------------------

app.include_router(usuario_router)
app.include_router(structure_router)
app.include_router(articulos_router)
app.include_router(documents_router)


# -------------------------------
# Root
# -------------------------------

@app.get("/")
def root():
    return {"Status": "ALIVE"}