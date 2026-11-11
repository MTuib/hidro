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
    API_ROOT = os.environ["API_ROOT"]
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
    def enviar_telegram(self, missatge: str):
        url = f"https://api.telegram.org/bot{self.TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": self.TELEGRAM_CHAT_ID,
            "text": missatge,
            "parse_mode": "Markdown",
        }

        try:
            self.session.post(url, data=data, timeout=10)
        except Exception as e:
            print(f"{self.ts()} ERROR Telegram: {e}")

    #API Login i consultes
    def login(self) -> bool:
        print(f"{self.ts()} Login API...")

        form = {
            "username": self.LOGIN_USER,
            "password": self.LOGIN_PASSWORD,
        }

        resp = self.session.post(self.LOGIN_URL, data=form, timeout=10)
        data = resp.json()

        if not data.get("access_token"):
            print(f"{self.ts()} Login fallit")
            return False

        self.jwt_token = data["access_token"]
        print(f"{self.ts()} Token actualitzat")
        return True

    def get_dispositiu_id(self, disp_nom: str) -> int | None:
        resp = self.session.get(
            self.DISPOSITIU_URL + disp_nom,
            headers=self.headers(),
            timeout=10
        )

        if resp.status_code == 401 and self.login():
            return self.get_dispositiu_id(disp_nom)

        if resp.status_code != 200:
            print(f"{self.ts()} Dispositiu no vàlid: {disp_nom}")
            return None

        return resp.json().get("id_disp")

    #Logica d'alertes
    def sonda_ha_publicat(self, sonda: str, hores: int) -> bool:
        ara = datetime.now(timezone.utc)
        temps_limit = ara - timedelta(hours=hores)

        disp_id = self.get_dispositiu_id(sonda)
        if disp_id is None:
            return False

        params = {"data_inici": temps_limit.isoformat()}
        url = f"{self.DADA_URL}/{disp_id}/"

        resp = self.session.get(url, headers=self.headers(), params=params, timeout=10)

        if resp.status_code != 200:
            print(f"{self.ts()} Error consultant dades de {sonda}")
            return False

        return len(resp.json()) > 0

    def pot_enviar_alerta(self, sonda: str) -> bool:
        avui = date.today()
        return self.alertes_enviades.get(sonda) != avui

    def marcar_alerta_enviada(self, sonda: str):
        self.alertes_enviades[sonda] = date.today()

    def comprovar_sonda(self, sonda: str, hores: int):
        if self.sonda_ha_publicat(sonda, hores):
            print(f"{self.ts()} OK → {sonda}")
            return

        if not self.pot_enviar_alerta(sonda):
            print(f"{self.ts()} Alerta ja enviada avui per {sonda}")
            return

        missatge = (
            "🚨 *ALERTA DE SONDA*\n\n"
            f"🕒 Data: {self.ts()}\n"
            f"📡 Sonda: {sonda}\n"
            f"⏰ Sense dades en les darreres {hores} hores\n"
            "❌ Revisar connexió, estat del dispositiu i carpeta *pendents*"
        )

        self.enviar_telegram(missatge)
        self.marcar_alerta_enviada(sonda)

    #TASCA PROGRAMADA
    def tasca_diaria(self):
        try:
            if not self.login():
                return

            sondes = [
                nom.strip()
                for nom in os.environ["ALERTA_SONDES"].split(",")
                if nom.strip()
            ]
            hores_permeses = int(os.environ["ALERTA_HORES"])

            for sonda in sondes:
                self.comprovar_sonda(sonda, hores_permeses)

        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
        ):
            print(f"{self.ts()} API no disponible")

            missatge = (
                "🚨 *ALERTA D'API*\n\n"
                f"🕒 Data: {self.ts()}\n"
                "❌ No s'ha pogut contactar amb l'API "
                "o s'ha superat el temps d'espera.\n"
                "La comprovació de les sondes ha quedat interrompuda."
            )

            self.enviar_telegram(missatge)


#MAIN
if __name__ == "__main__":
    AlertService().run(threading.Event())


