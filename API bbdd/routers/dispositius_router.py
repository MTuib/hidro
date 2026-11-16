from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.exc import MultipleResultsFound
from sqlalchemy.orm import Session
from bbdd.database import get_db
from bbdd.crud import get_dispositiu_by_nom, get_dispositiu_by_topic
from security.dependencies import (get_current_user,check_access)
from bbdd.schemas import DispositiuOut

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="usuaris/login")



@router.get("/", response_model=DispositiuOut)
async def obtenir_dispositiu_by_topic(
    topic: str = Query(..., min_length=1),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        dispositiu = get_dispositiu_by_topic(db, topic)
    except MultipleResultsFound:
        raise HTTPException(
            status_code=409,
            detail="Topic ambigu: hi ha més d'un dispositiu amb aquesta url",
        ) from None

    if dispositiu is None:
        raise HTTPException(status_code=404, detail="Dispositiu no trobat")

    check_access(db, user["id"], dispositiu.id_disp)
    return dispositiu


@router.get("/{nom_disp}", response_model=DispositiuOut)
async def obtenir_dispositiu_by_nom(
    nom_disp: str,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        dispositiu = get_dispositiu_by_nom(db, nom_disp)
    except MultipleResultsFound:
        raise HTTPException(
            status_code=409,
            detail="Nom de dispositiu ambigu: utilitzar la cerca pel topic complet",
        ) from None

    if not dispositiu:
        raise HTTPException(
            status_code=404,
            detail="Dispositiu no trobat",
        )

    check_access(
        db,
        user["id"],
        dispositiu.id_disp,
    )

    return dispositiu
