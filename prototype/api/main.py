from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

# =============================================================================
# UTILITIES IMPORT
# =============================================================================
# Env: gestisce le variabili d'ambiente da /workspace/.env
# DBConnPool: pool di connessioni database (SQLAlchemy)
# Questi import sono necessari per i moduli che accedono al database.
# Se nessun modulo usa il DB, il pool non viene inizializzato.
# =============================================================================
from utils.Env import Env
from utils.DBConnPool import DBConnPool

# =============================================================================
# MODULE ROUTERS IMPORT
# =============================================================================
# Ogni modulo espone un router FastAPI.
# I moduli che richiedono il database pool devono anche esporre init_pool().
# =============================================================================
from mod_status.routes import router as status_router

# =============================================================================
# DATABASE POOL INITIALIZATION REGISTRY
# =============================================================================
# Lista di tuple (module_routes, module_name) per i moduli che richiedono
# l'inizializzazione del database pool.
#
# Quando si aggiunge un modulo che usa il database:
# 1. Importare il modulo routes: from mod_xxx import routes as xxx_routes
# 2. Aggiungere alla lista: (xxx_routes, "mod_xxx")
#
# Esempio:
#   from mod_risorse import routes as risorse_routes
#   DB_MODULES = [
#       (risorse_routes, "mod_risorse"),
#   ]
# =============================================================================
DB_MODULES = [
    # (module_routes, "module_name"),
]

# =============================================================================
# DATABASE POOL (MODULE-LEVEL)
# =============================================================================
# Pool di connessioni condiviso tra tutti i moduli.
# Inizializzato solo se DB_MODULES non è vuoto.
# =============================================================================
db_pool: DBConnPool = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan: gestisce startup e shutdown.

    STARTUP:
    - Se ci sono moduli che richiedono il database (DB_MODULES non vuoto),
      inizializza il pool di connessioni e chiama init_pool() per ogni modulo.

    SHUTDOWN:
    - Chiude il pool di connessioni se era stato inizializzato.
    """
    global db_pool

    # Startup: inizializza database pool solo se necessario
    if DB_MODULES:
        env = Env("/workspace/.env")
        db_pool = DBConnPool(None, env)

        # Inizializza il pool per ogni modulo registrato
        for module_routes, module_name in DB_MODULES:
            if hasattr(module_routes, 'init_pool'):
                module_routes.init_pool(db_pool)

    yield

    # Shutdown: cleanup del pool se inizializzato
    if db_pool:
        db_pool.terminate()


app = FastAPI(
    title=os.getenv("PROJECT_NAME", "microservice"),
    version=os.getenv("VERSION", "1.0.0"),
    description="FastAPI Microservice Gateway",
    redirect_slashes=False,
    # Registra il gestore del ciclo di vita dell'applicazione
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# ROUTER REGISTRATION
# =============================================================================
# Registra i router dei moduli.
# - prefix: path base per tutte le route del modulo
# - tags: raggruppamento nella documentazione OpenAPI
#
# Nota: alcuni moduli (es. mod_risorse) definiscono il path completo nelle
# route stesse, quindi non richiedono prefix.
# =============================================================================
app.include_router(status_router, prefix="/api/status", tags=["status"])
