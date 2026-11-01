from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from bbdd.database import get_db
from bbdd.crud import get_dispositiu_by_nom
from security.dependencies import (get_current_user,check_access)
from bbdd.schemas import DispositiuOut

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="usuaris/login")



@router.get("/{nom_disp}", response_model=DispositiuOut)
async def obtenir_dispositiu_by_nom(
    nom_disp: str,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    dispositiu = get_dispositiu_by_nom(db, nom_disp)

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