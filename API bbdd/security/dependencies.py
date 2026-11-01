from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from security.jwt_manager import JWTmanager as jwt
from sqlalchemy.orm import Session
from bbdd.models import R_Projecte_Usuari, R_Projecte_Dispositiu

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="usuaris/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = jwt.verifyToken(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no vàlid",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload

def check_access(
    db: Session,
    id_usuari: int,
    id_disp: int,
):
    acces = (
        db.query(R_Projecte_Dispositiu.c.id_disp)
        .select_from(R_Projecte_Dispositiu)
        .join(
            R_Projecte_Usuari,
            R_Projecte_Usuari.c.id_proj
            == R_Projecte_Dispositiu.c.id_proj,
        )
        .filter(
            R_Projecte_Usuari.c.id_usuari == id_usuari,
            R_Projecte_Dispositiu.c.id_disp == id_disp,
        )
        .first()
    )

    if acces is None:
        raise HTTPException(
            status_code=403,
            detail="No tens permís per accedir a aquest dispositiu",
        )