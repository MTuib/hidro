# Subscriptor MQTT

Directori: `APP subscriptor`. Entrada: `monitor.py`.

Rep els missatges del topic configurat, resol el dispositiu a l'API pel nom del topic i intenta desar cada lectura nova. En cas de fallada, conserva el fitxer pendent.

Variables: `BROKER\_URL`, `BROKER\_PORT`, `BROKER\_TOPIC`, `MQTT\_USERNAME`, `MQTT\_PASSWORD`, `API\_ROOT`, `API\_USERNAME` i `API\_PASSWORD`. Les credencials MQTT i de l'API són diferents.

Dependències principals: paho-mqtt, Requests i python-dotenv.



## Activació dels avisos

|Variable|Valor que s'ha de configurar|
|-|-|
|`TELEGRAM\_BOT\_TOKEN`|Token del bot.|
|`TELEGRAM\_CHAT\_ID`|Identificador del xat o canal on el bot té permís per publicar.|
|`ALERTA\_SONDES`|Nom de la sonda, per defecte `00SONDA401`. Admet diversos noms separats per comes.|
|`ALERTA\_HORES`|Interval en hores per a les sondes de la llista. Valor inicial de 24.|
|`SMTP\_USER`|Adreça de Gmail que enviarà el correu.|
|`SMTP\_PASSWORD`|Contrasenya de `SMTP\_USER`.|
|`ALERTA\_DESTINATARIS`|Adreça de destinació o diverses adreces separades per comes.|

El subscriptor utilitza les credencials `API\_USERNAME` i `API\_PASSWORD` existents per consultar les sondes. El compte ha de tenir accés a cada dispositiu configurat. L'avís de Telegram utilitza el moment en què l'API ha desat cada registre. Una consulta correcta amb resultat buit genera l'avís. Un error de connexió, autenticació o permisos deixa la consulta pendent de reintent.



El correu informa del nombre de fitxers `.txt` que hi ha a la carpeta de pendents de `Backup` en el moment de la comprovació. L'enviament utilitza Gmail a través d'SMTP amb STARTTLS al port 587.



La comprovació es fa diàriament a les 07.00, hora de les Illes Balears. Si el servei inicia entre les 07.00 i les 07.59, fa la comprovació en arrencar. Els errors es tornen a provar cada cinc minuts dins aquesta franja. Si el servei està aturat tota l'hora, la comprovació següent serà l'endemà. La ingestió MQTT continua en el seu propi fil.

La fitxa diària de cada sonda i destinatari es desa a `pendents/.avisos.sqlite3` després d'una comprovació correcta, tant si tot està en ordre com si el servei extern ha acceptat l'avís. Mantén la carpeta de pendents en un volum persistent per conservar els registres de les comprovacions després de recrear el contenidor. Un reinici normal evita repetir una comprovació completada. Si la connexió cau just després d'un enviament i abans que se'n confirmi el resultat, el reintent podria repetir l'avís.

