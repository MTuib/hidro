# Subscriptor MQTT

Directori: `APP subscriptor`. Entrada: `monitor.py`.

Rep els missatges del topic configurat, resol el dispositiu a l'API pel nom del topic i intenta desar cada lectura nova. En cas de fallada, conserva el fitxer pendent.

Variables: `BROKER_URL`, `BROKER_PORT`, `BROKER_TOPIC`, `MQTT_USERNAME`, `MQTT_PASSWORD`, `API_ROOT`, `API_USERNAME` i `API_PASSWORD`. Les credencials MQTT i de l'API són diferents.

Dependències principals: paho-mqtt, Requests i python-dotenv.

