from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import datetime
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from bbdd.database import get_db
from bbdd.crud import create_dada, get_dades
from bbdd.schemas import DadaIngesta, DadaPayload
from security.jwt_manager import JWTmanager as jwt
from security.dependencies import (get_current_user, check_access)


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="usuaris/login")


@router.post("", status_code=status.HTTP_201_CREATED)
async def guardar_dada(
    data: DadaIngesta,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_access(db, user["id"], data.id_disp)
    try:
        create_dada(
            db=db,
            dada=data.payload,
            id_disp=data.id_disp
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    return {"detail": "Dada guardada correctament"}



@router.get("/{id_disp}/", response_model=list[DadaPayload])
async def llistar_dada(
    #id_proj: int,
    id_disp: int,
    data_inici: datetime = Query(None),
    data_final: datetime = Query(None),
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_access(db, user["id"], id_disp)
    print(f"Consultant dades per dispositiu {id_disp} entre {data_inici} i {data_final}")

    return get_dades(
        db=db,
        id_disp=id_disp,
        data_inici=data_inici,
        data_final=data_final
    )
