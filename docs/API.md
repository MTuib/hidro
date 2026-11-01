# API FastAPI

Directori: `API bbdd`. Entrada ASGI: `hidro_api:app`. Port de la guia: 8000.

L'API usa PostgreSQL, autentica amb JWT i comprova l'accés als dispositius a través dels projectes. El login és `POST /hidro/usuaris/login` amb formulari `username`/`password`. La documentació HTTP local és `/docs`.

Variables principals: `DATABASE_URL`, `JWT_SECRET_KEY`. El `.env` s'ha de carregar abans d'importar els routers i `bbdd.database`. La comanda del README ho fa explícitament, encara que un mòdul conservi una ruta relativa antiga de càrrega del `.env`.

Dependències principals: FastAPI, Uvicorn, SQLAlchemy, psycopg2-binary, Pydantic, python-jose, pwdlib/Argon2, python-multipart i python-dotenv. 

L'usuari tècnic del subscriptor també necessita un compte vigent i una relació amb el projecte de les sondes. Un 401 pot indicar credencials/token invàlids o compte caducat; un 403 pot indicar manca de relació amb el projecte.