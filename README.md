# Hidro — Plataforma de sondes IoT


Sistema per simular sondes, rebre'n les lectures per MQTT, desar-les a PostgreSQL mitjançant una API i consultar-les des d'un web Django.

| Component | Directori | Funció | Guia |
| --- | --- | --- | --- |
| API FastAPI | `API bbdd/` | Autenticació JWT, projectes, dispositius i lectures | [API](docs/API.md) |
| Web Django | `WEB site/labmanager/` | Login, taules, gràfics, filtres i CSV | [Web](docs/WEB.md) |
| Subscriptor MQTT | `APP subscriptor/` | Rep missatges i intenta desar les lectures noves a l'API | [Subscriptor](docs/SUBSCRIPTOR.md) |
| Simulador | `APP sonda/` | Genera dades de fins a vuit sondes | [Simulador](docs/SIMULADOR.md) |
| Esquema SQL | `SQL scripts/` | Estructura PostgreSQL i comprovacions de la càrrega inicial |

Les lectures segueixen el recorregut simulador → broker MQTT → subscriptor → API → PostgreSQL. El web consulta l'API des del servidor Django. PostgreSQL desa les lectures; el `db.sqlite3` de Django gestiona les seves taules internes.

## Estat funcional

- L'accés als dispositius depèn dels projectes associats al compte.
- Els filtres de dates del web corresponen a la **data de la lectura**. Una lectura del dia 26 desada el 27 apareix en filtrar el dia 26.
- La recuperació dels fitxers pendents, les alarmes i la revisió de la verificació TLS del broker estan ajornades. El subscriptor continua intentant desar les lectures noves.

## Requisits

- Python **3.12**. Entorn de referència comprovat: CPython **3.12.14**, Linux. Les instruccions de Windows s'han preparat.
- PostgreSQL i pgAdmin o psql.
- Accés al broker configurat i credencials vàlides per provar la recepció MQTT.
- Navegador web. Chart.js **4.5.1** s'inclou com a fitxer estàtic local amb la seva llicència.

`requirements.txt` fixa les dependències Python directes i transitives. `requirements-dev.txt` conté les mateixes versions més el client de proves HTTP. Els fitxers `.in` documenten les dependències directes i serveixen per regenerar els manifests després d'una revisió.

## Instal·lació nova a Windows / PowerShell

Executa les ordres des de l'arrel del projecte. Els exemples usen un entorn virtual nou anomenat `.venv`; si ja tens un entorn operatiu, conserva'l i prova aquesta instal·lació en una còpia separada.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pip check
```

Si només vols executar les aplicacions, pots instal·lar `requirements.txt` en lloc de `requirements-dev.txt`. No cal activar l'entorn: les ordres indiquen directament el seu intèrpret.


## Configuració compartida

Hi ha **un únic `.env` a l'arrel**. Per a una instal·lació nova, crea'l a partir de `.env.example` si encara no existeix:

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Emplena `DATABASE_URL`, `JWT_SECRET_KEY`, `DJANGO_SECRET_KEY`, `API_USERNAME`, `API_PASSWORD`, `MQTT_USERNAME` i `MQTT_PASSWORD` amb la configuració d'aquella instal·lació. El compte tècnic de l'API i el compte del broker són credencials de serveis diferents.

Per generar una clau aleatòria en una instal·lació nova, executa aquesta ordre una vegada per a cada clau secreta i copia cada resultat només al `.env` privat:

```powershell
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(64))"
```

En una instal·lació existent conserva les claus actuals. Les ordres d'arrencada següents carreguen explícitament el `.env` de l'arrel amb python-dotenv abans d'importar cada aplicació. `--no-override` conserva la prioritat de les variables ja definides al procés.

La guia usa API a `http://localhost:8000/hidro` i web a `http://127.0.0.1:8001/`. Mantén dos ports diferents. Si els canvies, actualitza també `API_ROOT` quan canviï el port de l'API.

## Preparar la base de dades

Per a una instal·lació nova:

1. Crea la base PostgreSQL buida amb pgAdmin i obre el Query Tool connectat a aquella base.
2. Executa `SQL scripts/creacio_bd.sql` des de `CREATE SCHEMA fis_disp;`. 
3. Configura `DATABASE_URL` perquè l'API apunti a aquella base.

Prepara també les taules internes de Django:

```powershell
.\.venv\Scripts\python.exe -m dotenv -f .env run --no-override -- .\.venv\Scripts\python.exe "WEB site/labmanager/manage.py" migrate
.\.venv\Scripts\python.exe -m dotenv -f .env run --no-override -- .\.venv\Scripts\python.exe "WEB site/labmanager/manage.py" check
```

## Arrencada local

Obre quatre terminals a l'arrel del projecte. En totes les ordres, el segon `python` ha de ser el del mateix entorn virtual; per evitar dependre del PATH, s'indica explícitament a continuació.

**1. API, port 8000**

```powershell
.\.venv\Scripts\python.exe -m dotenv -f .env run --no-override -- .\.venv\Scripts\python.exe -m uvicorn hidro_api:app --app-dir "API bbdd" --host 127.0.0.1 --port 8000
```

Documentació interactiva: `http://127.0.0.1:8000/docs`.

**2. Web, port 8001**

```powershell
.\.venv\Scripts\python.exe -m dotenv -f .env run --no-override -- .\.venv\Scripts\python.exe "WEB site/labmanager/manage.py" runserver 127.0.0.1:8001
```

Accedeix a `http://127.0.0.1:8001/login/` amb un compte creat a PostgreSQL per a l'API. El superusuari de l'admin Django és un compte diferent.

**3. Subscriptor**

```powershell
.\.venv\Scripts\python.exe -m dotenv -f .env run --no-override -- .\.venv\Scripts\python.exe "APP subscriptor/monitor.py"
```

**4. Simulador**

```powershell
.\.venv\Scripts\python.exe -m dotenv -f .env run --no-override -- .\.venv\Scripts\python.exe "APP sonda/cluster.py"
```

Comença creant una sonda i comprova'n una lectura abans de crear-ne més. Evita tenir obertes altres instàncies del mateix simulador o subscriptor.

Per aturar: usa `x` al simulador i Enter al monitor, segons els seus menús. Després atura web i API amb Ctrl+C.

## Verificació i lliurament

L'objectiu d'aquesta guia és el desenvolupament local. `DJANGO_ENV=production` requereix el desplegament HTTPS, el servidor d'aplicació i el servei d'estàtics; les ordres `runserver` d'aquí no constitueixen un desplegament de producció.
