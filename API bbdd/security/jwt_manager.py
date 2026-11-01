import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv
from jose import JWTError, jwt

load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=False)


class JWTmanager:
    SECRET_KEY = os.environ["JWT_SECRET_KEY"]
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

    if not SECRET_KEY.strip():
        raise RuntimeError("JWT_SECRET_KEY no pot estar buida.")

    @staticmethod
    def set_token(data: dict, expires_delta: timedelta | None = None, *, account_expires_at: datetime):
        if (not isinstance(account_expires_at, datetime)
                or account_expires_at.utcoffset() is None):
            raise ValueError("La caducitat ha de ser un datetime amb zona horària.")
        if (type(data.get("id")) is not int or data["id"] <= 0
                or not isinstance(data.get("user"), str) or not data["user"].strip()):
            raise ValueError("Identitat d'usuari no vàlida.")
        now = datetime.now(timezone.utc)
        maximum = timedelta(minutes=JWTmanager.ACCESS_TOKEN_EXPIRE_MINUTES)
        duration = maximum if expires_delta is None else expires_delta
        if not isinstance(duration, timedelta) or duration <= timedelta(0):
            raise ValueError("La durada del token ha de ser positiva.")
        deadline = account_expires_at.astimezone(timezone.utc)
        expiry = min(now + min(duration, maximum), deadline)
        exp = int(expiry.timestamp())
        if exp <= now.timestamp():
            raise ValueError("El compte ja no té prou vigència per emetre el token.")
        payload = data.copy()
        payload.update({"iat": int(now.timestamp()), "exp": exp, "termini": deadline.isoformat()})
        return jwt.encode(payload, JWTmanager.SECRET_KEY, algorithm=JWTmanager.ALGORITHM)

    @staticmethod
    def verifyToken(token: str):
        if not isinstance(token, str) or not token:
            return None
        try:
            payload = jwt.decode(
                token, JWTmanager.SECRET_KEY, algorithms=[JWTmanager.ALGORITHM],
                options={"require_exp": True, "leeway": 0},
            )
            if (type(payload.get("id")) is not int or payload["id"] <= 0
                    or not isinstance(payload.get("user"), str) or not payload["user"].strip()
                    or type(payload.get("exp")) is not int):
                return None
            now = datetime.now(timezone.utc)
            if now.timestamp() >= payload["exp"]:
                return None

            if "termini" in payload:
                deadline = datetime.fromisoformat(payload["termini"])
                if deadline.utcoffset() is None:
                    return None
                deadline = deadline.astimezone(timezone.utc)
                if now >= deadline or payload["exp"] > deadline.timestamp():
                    return None
            return payload
        except (JWTError, ValueError, TypeError, OverflowError):
            return None
