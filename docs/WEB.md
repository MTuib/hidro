# Web Django

Directori: `WEB site/labmanager`. Entrada: `manage.py`. Port de la guia: 8001.

El navegador parla amb Django i Django consulta l'API indicada per `API_ROOT`. La sessió funcional usa el JWT de l'API en una cookie HttpOnly. El login de la plataforma no és el login de l'administració Django.

Variables: `API_ROOT`, `DJANGO_SECRET_KEY`, `DJANGO_ENV`, `DJANGO_ALLOWED_HOSTS` i les opcions HTTPS/CSRF documentades a `.env.example`.

Dependències principals: Django, Requests i python-dotenv. Chart.js 4.5.1 es distribueix a `core/static/vendor/chartjs/`, i la plantilla base el carrega abans de `devices/static/js/script.js`.

El filtre segueix la data escrita a cada lectura. Les sondes simulades generen una data local sense zona horària. Django encara rep tot l'historial d'aquell dispositiu des de l'API abans de filtrar-lo. La taula mostra 10 files per pàgina; la gràfica correspon a la magnitud seleccionada i el CSV conserva les magnituds del període filtrat.

Les migracions Django preparen les seves taules internes. No substitueixen `creacio_bd.sql` de PostgreSQL. El compte funcional del web és el de l'API.
