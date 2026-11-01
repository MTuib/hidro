import os
from dotenv import load_dotenv
from subscriber import Subscriber


#######################################
#Dades de connexio al broker MQTT#
#######################################
load_dotenv()

BROKER = os.environ["BROKER_URL"]
PORT = int(os.environ["BROKER_PORT"])
TOPIC = os.environ["BROKER_TOPIC"]


USERNAME = os.environ["MQTT_USERNAME"]
PASSWORD = os.environ["MQTT_PASSWORD"]
#######################################
print("---------------------------------------")
print("Iniciant Monitor del Subscriptor al Broker MQTT")
print("---------------------------------------")
print("Aquest monitor està subscrit al topic hidro/aquifers/#")
print("Per tant recull les dades publicades per totes les sondes dels aqüifers")
print("Cada missatge rebut del broker MQTT s'executa en un thread independet")
print("La connexió amb el broker es realitza de forma segura mitjançant TLS")
print("TLS usa usuari i contrasenya per a l'autenticació però no usa certificats")
print("En cas de desconnexió amb el broker MQTT el monitor intenta la reconnexió cada 10 minuts")
print("---------------------------------------")
print("Prem Enter per aturar el monitor\n")

#Crear i iniciar el Subscriber
mode = "db"  #Mode de funcionament: "print" per imprimir missatges sense bbdd, "db" per guardar a la base de dades
subscriber = Subscriber(BROKER, PORT, TOPIC, USERNAME, PASSWORD, mode)
subscriber.start()

#Esperar a que l'usuari premi Enter per aturar el monitor
input("")
subscriber.stop()
print("Monitor aturat.")