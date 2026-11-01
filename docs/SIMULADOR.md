# Simulador de sondes

Directori: `APP sonda`. Entrada: `cluster.py`.

El menú permet crear fins a vuit sondes `00SONDA001`–`00SONDA008`. Cada sonda treballa en un fil i publica dades aleatòries al topic `hidro/aquifers/{ID_SONDA}/dades`, amb QoS 0. `newRegistre()` dedica aproximadament 40 segons a preparar 23 files i `run()` espera després 50–70 segons. L’interval entre publicacions és, per tant, aproximadament de 90–110 segons més el temps de connexió; la primera publicació també espera la generació del primer missatge.

Variables principals de connexió: `BROKER_URL`, `BROKER_PORT`, `MQTT_USERNAME` i `MQTT_PASSWORD`, segons la lectura del `.env`

Dependències principals: paho-mqtt i python-dotenv.

Per sortir, escriu `x`.



