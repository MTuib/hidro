import os

import requests


class JWTExpired(Exception):
    pass


class APIError(Exception):
    def __init__(self, message, status_code=502):
        super().__init__(message)
        self.status_code = status_code


class APIClient:
    #Connexió i inactivitat de lectura
    HTTP_TIMEOUT = (3, 10)

    def __init__(self, token=None):
        self.base_url = os.environ.get(
            "API_ROOT", "http://localhost:8000/hidro"
        ).rstrip("/") + "/"
        self.headers = {"Accept": "application/json"}
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    @staticmethod
    def validate_token(response):
        if response.status_code == 401:
            raise JWTExpired("La sessió ha caducat. Torna a iniciar sessió.")

    def _request(self, method, path, *, login=False, validator, **kwargs):
        try:
            response = requests.request(
                method, self.base_url + path, headers=self.headers,
                timeout=self.HTTP_TIMEOUT, allow_redirects=False, **kwargs,
            )
        except requests.exceptions.Timeout as exc:
            raise APIError("L'API tarda massa a respondre.", 504) from exc
        except requests.exceptions.RequestException as exc:
            raise APIError("No es pot connectar amb l'API", 503) from exc

        if login and response.status_code == 401:
            message = "Usuari o contrasenya incorrectes."
            try:
                body = response.json()
            except ValueError:
                body = None
            detail = body.get("detail") if isinstance(body, dict) else None
            code = detail.get("code") if isinstance(detail, dict) else None
            if code == "account_expired":
                message = "El compte ha caducat"
            elif code == "account_expiry_invalid":
                message = "El compte no té una caducitat vàlida"
            raise APIError(message, 401)
        if not login:
            self.validate_token(response)
        status = response.status_code
        if status != 200:
            messages = {
                403: "No tens permisos per accedir a aquest recurs.",
                404: "No s'ha trobat el recurs sol·licitat.",
                429: "Hi ha massa peticions.",
                503: "L'API no està disponible.",
                504: "L'API tarda massa a respondre.",
            }
            web_status = status if status in messages else 502
            raise APIError(messages.get(status, "L'API ha retornat una resposta inesperada."), web_status)
        try:
            payload = response.json()
        except ValueError as exc:
            raise APIError("L'API no ha retornat un JSON vàlid.") from exc
        if not validator(payload):
            raise APIError("L'API ha retornat dades amb un format inseperat.")
        return response

    @staticmethod
    def _entity(payload, id_field):
        return (
            isinstance(payload, dict)
            and type(payload.get(id_field)) is int
            and isinstance(payload.get("nom"), str)
        )

    def login(self, username, password):
        response = self._request(
            "POST", "usuaris/login", login=True,
            data={"username": username, "password": password},
            validator=lambda p: isinstance(p, dict)
            and isinstance(p.get("access_token"), str)
            and bool(p["access_token"].strip()),
        )
        return {"access_token": response.json()["access_token"]}

    def get_projects(self):
        return self._request(
            "GET", "projectes/", validator=lambda p: isinstance(p, list)
            and all(self._entity(row, "id_proj") for row in p),
        )

    def get_project_detail(self, project_id):
        return self._request(
            "GET", f"projectes/{project_id}",
            validator=lambda p: self._entity(p, "id_proj"),
        )

    def get_devices(self, project_id):
        return self._request(
            "GET", f"projectes/{project_id}/dispositius",
            validator=lambda p: isinstance(p, list)
            and all(self._entity(row, "id_disp") for row in p),
        )

    def get_device_detail(self, project_id, device_id):
        return self._request(
            "GET", f"projectes/{project_id}/{device_id}",
            validator=lambda p: self._entity(p, "id_disp"),
        )

    def get_dades(self, project_id, device_id, data_inici=None, data_final=None):
        params = {}
        if data_inici:
            params["data_inici"] = data_inici
        if data_final:
            params["data_final"] = data_final
        return self._request(
            "GET", f"projectes/{project_id}/{device_id}/dades", params=params,
            validator=lambda p: isinstance(p, list) and all(
                isinstance(row, str)
                or (isinstance(row, dict) and isinstance(row.get("dada"), str))
                for row in p
            ),
        )
