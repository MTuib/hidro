from datetime import datetime, timedelta, timezone, date
import time
import requests
import schedule
import os
from pathlib import Path
from dotenv import load_dotenv
import threading

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

class AlertService:
    # Configuració API i Telegram
    API_ROOT = os.environ["API_ROOT"].strip().rstrip("/")
    LOGIN_URL = f"{API_ROOT}/usuaris/login"
    DISPOSITIU_URL = f"{API_ROOT}/dispositius/"
    DADA_URL = f"{API_ROOT}/dada"

    LOGIN_USER = os.environ["API_USERNAME"]
    LOGIN_PASSWORD = os.environ["API_PASSWORD"]

    TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
    TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
    #########################################

    def __init__(self):
        self.session = requests.Session()
        self.jwt_token: str | None = None
        self.alertes_enviades: dict[str, date] = {}

    #SERVEI
    def run(self, stop_event: threading.Event):
        programador = schedule.Scheduler()
        programador.every().day.at("07:00").do(self.tasca_diaria)

        self.enviar_telegram("🤖 Servei d'alertes actiu. Comprovació diària a les 07:00.")

        while not stop_event.is_set():
            programador.run_pending()
            stop_event.wait(60)

    #Útils
    @staticmethod
    def ts() -> str:
        return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    def headers(self) -> dict:
        return {"Authorization": f"Bearer {self.jwt_token}"}


    #Telegram
    def enviar_telegram(self, missatge: str) -> bool:
        url = f"https://api.telegram.org/bot{self.TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": self.TELEGRAM_CHAT_ID,
            "text": missatge,
        }

        try:
            resp = self.session.post(url, data=data, timeout=10)
            if resp.status_code == 200 and resp.json().get("ok") is True:
                return True
            print(f"{self.ts()} Telegram no ha confirmat l'enviament")
        except (requests.exceptions.RequestException, ValueError, AttributeError):
            print(f"{self.ts()} ERROR en l'enviament a Telegram")
        return False

    #API Login i consultes
    def login(self) -> bool:
        print(f"{self.ts()} Login API...")

        form = {
            "username": self.LOGIN_USER,
            "password": self.LOGIN_PASSWORD,
        }

        resp = self.session.post(self.LOGIN_URL, data=form, timeout=10)
        if resp.status_code != 200:
            print(f"{self.ts()} Login fallit: HTTP {resp.status_code}")
            return False
        try:
            data = resp.json()
        except ValueError:
            print(f"{self.ts()} Resposta de login no vàlida")
            return False
        token = data.get("access_token") if isinstance(data, dict) else None
        if not isinstance(token, str) or not token.strip():
            print(f"{self.ts()} Login fallit")
            return False

        self.jwt_token = token
        print(f"{self.ts()} Token actualitzat")
        return True

    def get_dispositiu_id(self, sonda: str) -> int | None:
        #Degut a modificació de la BBDD és manté l'identificació per topic i per nom. 
        #Un tòpic complet conté '/'. Els noms antics només s'accepten si són únics.
        per_topic = "/" in sonda
        url = self.DISPOSITIU_URL if per_topic else self.DISPOSITIU_URL + sonda
        params = {"topic": sonda} if per_topic else None
        for intent in range(2):
            resp = self.session.get(
                url, params=params, headers=self.headers(), timeout=10
            )
            if resp.status_code == 401 and intent == 0 and self.login():
                continue
            if resp.status_code != 200:
                print(f"{self.ts()} No es pot identificar {sonda}: HTTP {resp.status_code}")
                return None
            try:
                data = resp.json()
            except ValueError:
                return None
            disp_id = data.get("id_disp") if isinstance(data, dict) else None
            return disp_id if type(disp_id) is int else None
        return None

    #Logica d'alertes
    def sonda_ha_publicat(self, sonda: str, hores: int) -> bool | None:
        ara = datetime.now(timezone.utc)
        temps_limit = ara - timedelta(hours=hores)

        disp_id = self.get_dispositiu_id(sonda)
        if disp_id is None:
            return None

        params = {"data_inici": temps_limit.isoformat()}
        url = f"{self.DADA_URL}/{disp_id}/"

        resp = self.session.get(url, headers=self.headers(), params=params, timeout=10)

        if resp.status_code != 200:
            print(f"{self.ts()} Error consultant dades de {sonda}")
            return None

        try:
            dades = resp.json()
        except ValueError:
            return None
        return bool(dades) if isinstance(dades, list) else None

    def pot_enviar_alerta(self, sonda: str) -> bool:
        avui = date.today()
        return self.alertes_enviades.get(sonda) != avui

    def marcar_alerta_enviada(self, sonda: str):
        self.alertes_enviades[sonda] = date.today()

    def comprovar_sonda(self, sonda: str, hores: int):
        ha_publicat = self.sonda_ha_publicat(sonda, hores)
        if ha_publicat is None:
            print(f"{self.ts()} Comprovació de {sonda} no completada; no es genera avís d'inactivitat")
            return
        if ha_publicat:
            print(f"{self.ts()} OK → {sonda}")
            return

        if not self.pot_enviar_alerta(sonda):
            print(f"{self.ts()} Alerta ja enviada avui per {sonda}")
            return

        missatge = (
            "🚨 ALERTA DE SONDA\n\n"
            f"🕒 Data: {self.ts()}\n"
            f"📡 Sonda: {sonda}\n"
            f"⏰ Sense dades en les darreres {hores} hores\n"
            "❌ Revisar connexió, estat del dispositiu i carpeta pendents"
        )

        if self.enviar_telegram(missatge):
            self.marcar_alerta_enviada(sonda)

    #TASCA PROGRAMADA
    def tasca_diaria(self):
        try:
            if not self.login():
                return

            topics = os.getenv("ALERTA_TOPICS", "").strip()
            configuracio = topics or os.getenv("ALERTA_SONDES", "")
            sondes = [nom.strip() for nom in configuracio.split(",") if nom.strip()]
            hores_permeses = int(os.environ["ALERTA_HORES"])

            for sonda in sondes:
                self.comprovar_sonda(sonda, hores_permeses)

        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
        ):
            print(f"{self.ts()} API no disponible")

            missatge = (
                "🚨 ALERTA D'API\n\n"
                f"🕒 Data: {self.ts()}\n"
                "❌ No s'ha pogut contactar amb l'API "
                "o s'ha superat el temps d'espera.\n"
                "La comprovació de les sondes ha quedat interrompuda."
            )

            self.enviar_telegram(missatge)


#MAIN
if __name__ == "__main__":
    AlertService().run(threading.Event())


