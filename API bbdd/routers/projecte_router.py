from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from bbdd.database import get_db
from bbdd.crud import get_projectes_by_usuari, get_dispositius_by_usuari_projecte, get_dades
from bbdd.schemas import DispositiuOut, ProjecteBase, DadaPayload
from security.jwt_manager import JWTmanager as jwt
from security.dependencies import get_current_user

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="usuaris/login")


@router.get("/")
async def get_llista_projectes(
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_projectes_by_usuari(db, user["id"])


@router.get("/{id_proj}", response_model=ProjecteBase)
async def get_detall_projecte(id_proj: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    projectes = obtenir_llista_projectes_usuari(db, token)

    for projecte in projectes:
        if projecte.id_proj == id_proj:
            return projecte

    raise HTTPException(status_code=404, detail="Projecte no trobat")


@router.get("/{id_proj}/dispositius", response_model=list[DispositiuOut])
async def obtenir_dispositius_by_usuari_projecte_endpoint(
    id_proj: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    return obtenir_dispositius_usuari_projecte(db, token, id_proj)


@router.get("/{id_proj}/{id_disp}", response_model=DispositiuOut)
async def detall_dispositiu(
    id_proj: int,
    id_disp: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    dispositius = obtenir_dispositius_usuari_projecte(db, token, id_proj)

    for dispositiu in dispositius:
        if dispositiu.id_disp == id_disp:
            return dispositiu

    raise HTTPException(status_code=404, detail="Dispositiu no trobat")

@router.get("/{id_proj}/{id_disp}/dades", response_model=list[DadaPayload])
async def llistar_dada(
    id_proj: int,
    id_disp: int,
    data_inici: datetime = Query(None),
    data_final: datetime = Query(None),
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    if not jwt.verifyToken(token):
        raise HTTPException(status_code=401, detail="Token no vàlid")

    payload = jwt.verifyToken(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Token no vàlid")

    id_usuari = payload["id"]

    dispositius = get_dispositius_by_usuari_projecte(db, id_usuari, id_proj)

    if not any(d.id_disp == id_disp for d in dispositius):
        raise HTTPException(status_code=403, detail="Accés denegat")

    return get_dades(
        db=db,
        id_disp=id_disp,
        data_inici=data_inici,
        data_final=data_final
    )

#Funcions auxiliars de servei
def obtenir_dispositius_usuari_projecte(db: Session, token: str, id_proj: int):
    if not jwt.verifyToken(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no vàlid",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = jwt.verifyToken(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Token no vàlid")

    id_usuari = payload["id"]
    
    return get_dispositius_by_usuari_projecte(db, id_usuari, id_proj)


def obtenir_llista_projectes_usuari(db: Session, token: str):
    if not jwt.verifyToken(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no vàlid",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = jwt.verifyToken(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Token no vàlid")

    id_usuari = payload["id"]

    return get_projectes_by_usuari(db, id_usuari)