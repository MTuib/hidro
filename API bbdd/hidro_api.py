from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env", override=False)

from fastapi import FastAPI, Depends
from routers import usuaris_router, dispositius_router, dada_router, projecte_router
from security.account_status import require_active_account

app = FastAPI(
    title="API REST  Sistema de Monitoratge Hidrològic",
    description="""
    API encarregada de la persistència i consulta de dades
    provinents de sondes hidrològiques via MQTT.
    """,
    version="1.0.0",
    contact={
        "name": "Miquel Taberner Salas",
        "email": "mtaberner@gmail.com",
    }
)

#Rutes projecte HIDRO
app.include_router(usuaris_router.router, prefix="/hidro/usuaris", tags=["usuaris"])
app.include_router(dispositius_router.router, dependencies=[Depends(require_active_account)], prefix="/hidro/dispositius", tags=["dispositius"])
app.include_router(dada_router.router, dependencies=[Depends(require_active_account)], prefix="/hidro/dada", tags=["dada"])
app.include_router(projecte_router.router, dependencies=[Depends(require_active_account)], prefix="/hidro/projectes", tags=["projectes"])