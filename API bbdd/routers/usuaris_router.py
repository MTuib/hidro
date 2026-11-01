from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from bbdd.crud import get_user_by_name
from bbdd.database import get_db
from security.account_status import account_deadline, account_error
from security.hashing import verify_password
from security.jwt_manager import JWTmanager as jwt

router = APIRouter()
ACCESS_TOKEN_EXPIRE_MINUTES = 30


@router.post("/login")
async def login(data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_name(db, data.username)
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=401, detail="Usuari o contrasenya incorrectes",
            headers={"WWW-Authenticate": "Bearer"},
        )
    deadline = account_deadline(user)
    try:
        token = jwt.set_token(
            data={"user": user.nom, "id": user.id_usuari},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
            account_expires_at=deadline,
        )
    except ValueError as exc:
        raise account_error("account_expired", "El compte ha caducat.") from exc
    return {"access_token": token, "token_type": "bearer"}
