from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, date
import threading
import os


class Alarma(threading.Thread):
    DESTINATARIS = [os.environ["ALERTA_DESTINATARIS"]]
    def __init__(self, stop_event: threading.Event):
        super().__init__(daemon=True)
        self.stop_event = stop_event

        base_dir = Path(__file__).resolve().parent
        self.pendents_dir = base_dir / "pendents"

        self.remitent = os.environ["SMTP_USER"]
        self.contrasenya = os.environ["SMTP_PASSWORD"]

        self.ultima_data_enviada: date | None = None

    def enviar_email(self):
        subject = "Hidro: Dades pendents de guardar"
        body = (
            "S'han detectat dades pendents de guardar a la BBDD "
            "dins la carpeta /pendents."
        )

        msg = MIMEMultipart()
        msg["From"] = self.remitent
        msg["To"] = ", ".join(self.DESTINATARIS)
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(self.remitent, self.contrasenya)
            server.sendmail(self.remitent, self.DESTINATARIS, msg.as_string())
            server.quit()
            print("Alarma enviada correctament")
        except Exception as e:
            print(f"Error enviant alarma: {e}")

    def hi_ha_pendents(self) -> bool:
        return self.pendents_dir.exists() and any(self.pendents_dir.iterdir())

    def run(self):
        print("Monitor d'alarmes iniciat")

        while not self.stop_event.is_set():
            ara = datetime.now()

            if ara.hour == 7:
                avui = ara.date()
                if self.ultima_data_enviada != avui and self.hi_ha_pendents():
                    self.enviar_email()
                    self.ultima_data_enviada = avui

            self.stop_event.wait(3600)
