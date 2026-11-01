from datetime import datetime, timezone

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from bbdd.database import get_db
from bbdd.models import Usuari
from security.jwt_manager import JWTmanager

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/hidro/usuaris/login")


def account_error(code, message):
    return HTTPException(
        status_code=401, detail={"code": code, "message": message},
        headers={"WWW-Authenticate": "Bearer"},
    )


def account_deadline(user):
    deadline = user.caducitat
    if not isinstance(deadline, datetime) or deadline.utcoffset() is None:
        raise account_error("account_expiry_invalid", "El compte no té una caducitat vàlida.")
    deadline = deadline.astimezone(timezone.utc)
    if datetime.now(timezone.utc) >= deadline:
        raise account_error("account_expired", "El compte ha caducat.")
    return deadline


def require_active_account(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db),
):
    payload = JWTmanager.verifyToken(token)
    if payload is None:
        raise account_error("invalid_token", "Token no vàlid o caducat.")
    user = db.query(Usuari).filter(Usuari.id_usuari == payload["id"]).first()
    if user is None:
        raise account_error("invalid_account", "El compte ja no està disponible.")
    account_deadline(user)
    return payload
