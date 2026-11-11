import os
import threading
import ssl
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit

from dotenv import load_dotenv
import requests
import paho.mqtt.client as mqtt


load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from backup import Backup
from APPmonitoreig.alarma import Alarma
from APPmonitoreig.telegram import AlertService


class Subscriber:
    API_ROOT = os.getenv("API_ROOT", "http://localhost:8000/hidro").strip().rstrip("/")
    if urlsplit(API_ROOT).scheme not in ("http", "https") or not urlsplit(API_ROOT).hostname:
        raise ValueError(
            "API_ROOT no conté una URL completa, "
            "per exemple http://localhost:8000/hidro"
        )

    LOGIN_URL = f"{API_ROOT}/usuaris/login"
    DISPOSITIU_URL = f"{API_ROOT}/dispositius/"
    DADA_URL = f"{API_ROOT}/dada"

    LOGIN_USER = os.environ["API_USERNAME"]
    LOGIN_PASSWORD = os.environ["API_PASSWORD"]
    #Temps de connexio i d'espera de dades
    HTTP_TIMEOUT = (3, 5)

    def __init__(self, broker, port, topic, username, password, mode="db"):
        self.broker = broker
        self.port = port
        self.topic = topic
        self.mode = mode

        self.jwt_token = None
        self.session = requests.Session()
        self.backup = Backup()

        #Inicialitzar alarma i servei d'alertes
        self.stop_event = threading.Event()
        self.alarma = Alarma(self.stop_event)
        self.alarma.start()

        self.servei_alertes = AlertService()
        self.fil_alertes = threading.Thread(
            target=self.servei_alertes.run,
            args=(self.stop_event,),
            daemon=True,
        )
        self.fil_alertes.start()
        ###########################

        self.client = mqtt.Client(
            client_id="hidro_subscriber",
            clean_session=False,
        )
        self.client.username_pw_set(username, password)
        self.client.tls_set(cert_reqs=ssl.CERT_NONE)
        self.client.tls_insecure_set(True)

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

        self.client.reconnect_delay_set(min_delay=1, max_delay=120)

    #MQTT CALLBACKS
    def on_connect(self, client, userdata, flags, rc):
        missatges = {
            0: "Connectat correctament",
            1: "Protocol incorrecte",
            2: "Client ID incorrecte",
            3: "Broker no disponible",
            4: "Usuari no autoritzat",
            5: "Contrasenya incorrecta",
        }

        print(f"{self._ts()} MQTT: {missatges.get(rc, 'Error desconegut')}")

        if rc == 0:
            client.subscribe(self.topic)
            print(f"{self._ts()} Subscrit a {self.topic}")

    def on_message(self, client, userdata, msg):
        threading.Thread(
            target=self.processar_missatge,
            args=(msg,),
            daemon=True,
        ).start()

    def on_disconnect(self, client, userdata, rc):
        print(f"{self._ts()} MQTT desconnectat")

    #PROCESSAMENT
    def processar_missatge(self, msg):
        print(f"{self._ts()} Missatge rebut: {msg.topic}")

        backup_path = self.backup.crear_backup(msg)

        if self.mode == "print":
            print(msg.payload.decode(errors="ignore"))
            return

        try:
            guardada = self.guardar_dada_db(msg)
        except requests.exceptions.Timeout:
            print(f"{self._ts()} Temps d'espera de l'API esgotat")
            guardada = False
        except requests.exceptions.ConnectionError:
            print(f"{self._ts()} No s'ha pogut connectar amb l'API")
            guardada = False
        except requests.exceptions.RequestException as exc:
            print(f"{self._ts()} Error en la peticio a l'API: {type(exc).__name__}")
            guardada = False

        if guardada:
            Backup.eliminar_backup(backup_path)
        else:
            print(f"{self._ts()} Dada pendent d'enviar: {backup_path}")

    #API
    def login(self) -> bool:
        form = {
            "username": self.LOGIN_USER,
            "password": self.LOGIN_PASSWORD,
        }

        resp = self.session.post(
            self.LOGIN_URL,
            data=form,
            timeout=self.HTTP_TIMEOUT,
        )

        if resp.status_code != 200:
            print(f"{self._ts()} Login fallit: HTTP {resp.status_code}")
            return False

        try:
            data = resp.json()
        except ValueError:
            print(f"{self._ts()} El login no ha retornat un JSON valid")
            return False

        token = data.get("access_token") if isinstance(data, dict) else None
        if not isinstance(token, str) or not token.strip():
            print(f"{self._ts()} Login sense un access_token valid")
            return False

        self.jwt_token = token
        print(f"{self._ts()} Token actualitzat")
        return True

    def guardar_dada_db(self, msg) -> bool:
        parts = msg.topic.split("/")
        if len(parts) < 3 or not parts[2]:
            print(f"{self._ts()} Topic incorrecte")
            return False

        disp_nom = parts[2]

        if not self.jwt_token and not self.login():
            return False

        for intent in range(2):
            disp_resp = self.session.get(
                self.DISPOSITIU_URL + disp_nom,
                headers=self._headers(),
                timeout=self.HTTP_TIMEOUT,
            )

            if disp_resp.status_code == 401 and intent == 0:
                if self.login():
                    continue
                return False

            if disp_resp.status_code != 200:
                print(
                    f"{self._ts()} No s'ha pogut consultar el dispositiu: "
                    f"HTTP {disp_resp.status_code}"
                )
                return False

            try:
                dispositiu = disp_resp.json()
            except ValueError:
                print(f"{self._ts()} La consulta del dispositiu no ha retornat un JSON valid")
                return False

            id_disp = dispositiu.get("id_disp") if isinstance(dispositiu, dict) else None
            if not isinstance(id_disp, int) or isinstance(id_disp, bool):
                print(f"{self._ts()} Resposta del dispositiu sense un id_disp valid")
                return False

            body = {
                "payload": msg.payload.decode(errors="ignore"),
                "id_disp": id_disp,
            }

            resp = self.session.post(
                self.DADA_URL,
                json=body,
                headers=self._headers(),
                timeout=self.HTTP_TIMEOUT,
            )

            if resp.status_code == 201:
                return True

            if resp.status_code == 401 and intent == 0:
                if self.login():
                    continue
                return False

            print(f"{self._ts()} No s'ha pogut guardar la dada: HTTP {resp.status_code}")
            return False

        return False

    #CONTROL
    def start(self):
        self.client.connect(self.broker, self.port)
        self.client.loop_start()

    def stop(self):
        self.stop_event.set()
        self.client.loop_stop()
        self.client.disconnect()

    def _headers(self):
        return {"Authorization": f"Bearer {self.jwt_token}"}

    @staticmethod
    def _ts():
        return datetime.now().strftime("%d/%m/%Y %H:%M:%S")
