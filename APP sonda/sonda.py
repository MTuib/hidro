import threading
import paho.mqtt.client as mqtt
import ssl
import random
import os
from dotenv import load_dotenv
from datetime import datetime


class Sonda(threading.Thread):
    #Variables golbals de totes les sondes
    load_dotenv()
    BROKER = os.environ["BROKER_URL"]    
    PORT = int(os.environ["BROKER_PORT"])
    TOPIC_ROOT = "hidro/aquifers/"
    USERNAME = os.environ["MQTT_USERNAME"]
    PASSWORD = os.environ["MQTT_PASSWORD"]

    #Textos descriptius de les variables
    text_Profunditat = "Nivell"
    text_Temperatura = "Temperatura"
    text_Conductivitat = "Conductivitat"
    text_Salinitat = "Salinity"
    text_Tds = "TDS"
    text_Amperatge = "Consum"
    text_Signal = "Signal"
    text_Voltatge = "Voltatge"

    def __init__(self, id, stop_event):
        super().__init__()
        self.id = id

        # Event per aturar el thread
        self.stop_event = stop_event

        # Configuracio del client MQTT amb ID de client unic
        self.client = mqtt.Client(client_id=self.id, clean_session=True)

        # Configuracio de la connexio segura TLS i autenticacio
        self.client.tls_set(cert_reqs=ssl.CERT_NONE)
        self.client.tls_insecure_set(True)
        self.client.username_pw_set(self.USERNAME, self.PASSWORD)
    
    def run(self):
        while not self.stop_event.is_set():
            self.sendData()
            #Espera entra 50 i 70 segons per a la propera transmissio
            self.stop_event.wait(random.randint(50,70))
    
    #MÈTODES
    def sendData(self):
        try:
            self.client.connect(self.BROKER, self.PORT, 60)
            missatge = self.newRegistre()
            topic = self.TOPIC_ROOT + self.id +"/dades" #Exemple de topic vàlid: hidro/aquifers/00SONDA401/dades
            self.client.publish(topic, missatge)
            print(f"{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}: Missatge publicat des de {self.id}")
            self.client.disconnect()
        except Exception as e:
            print(f"Error enviant dades desde {self.id}: {e}")

    def on_log(self, client, userdata, level, buf):
        print(f"Log: {buf}")

    #Un registre conte 4 mostres de les magnituds principals i 1 mostra de les magnituds secundaries
    def newRegistre(self):
        niv = []
        temp = []
        conduc = []
        salin = []
        tds = []
        amper = []
        signal = []
        volt = []
            
        for i in range(4): #4 mostres per registre
            niv.append(self.newNivell())
            temp.append(self.newTempertaura())
            conduc.append(self.newConductivitat()) 
            salin.append(self.newSalinitat())
            tds.append(self.newTds())

            #Espera 10 segons per a la propera mostra
            self.stop_event.wait(10)

        #Aquestes magnituds es mostretgen amb menys frequencia
        amper.append(self.newAmperatge())
        signal.append(self.newSignal())
        volt.append(self.newVoltatge())
        
        registre="".join(niv)+ "".join(temp)+ "".join(conduc)+ "".join(salin)+ "".join(tds)+ "".join(amper)+ "".join(signal)+ "".join(volt)

        return registre

    #Mètodes per generar noves dades simulades
    def newTempertaura(self):
        temp = self.id+";"+self.text_Temperatura+";"+datetime.now().strftime("%d/%m/%Y %H:%M:%S")+";"+str(round(random.uniform(-10.0, 40.0),2))+"\n"
        return temp
    
    def newNivell(self):
        return self.id+";"+self.text_Profunditat+";"+datetime.now().strftime("%d/%m/%Y %H:%M:%S")+";"+str(round(random.uniform(0.0, 10.0),2))+"\n"
    
    def newConductivitat(self):
        return self.id+";"+self.text_Conductivitat+";"+datetime.now().strftime("%d/%m/%Y %H:%M:%S")+";"+str(round(random.uniform(0.0, 50.0),2))+"\n"
    
    def newSalinitat(self):
        return self.id+";"+self.text_Salinitat+";"+datetime.now().strftime("%d/%m/%Y %H:%M:%S")+";"+str(round(random.uniform(0.0, 35.0),2))+"\n"
    
    def newTds(self):
        return self.id+";"+self.text_Tds+";"+datetime.now().strftime("%d/%m/%Y %H:%M:%S")+";"+str(round(random.uniform(0.0, 500.0),2))+"\n"
    
    def newAmperatge(self):
        return self.id+";"+self.text_Amperatge+";"+datetime.now().strftime("%d/%m/%Y %H:%M:%S")+";"+str(round(random.uniform(0.0, 100.0),2))+"\n" 

    def newSignal(self):
        return self.id+";"+self.text_Signal+";"+datetime.now().strftime("%d/%m/%Y %H:%M:%S")+";"+str(round(random.uniform(0.0, 100.0),2))+"\n"
    
    def newVoltatge(self):
        return self.id+";"+self.text_Voltatge+";"+datetime.now().strftime("%d/%m/%Y %H:%M:%S")+";"+str(round(random.uniform(0.0, 100.0),2))+"\n"  