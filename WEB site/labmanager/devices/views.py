import csv
import io
import math
import re
from datetime import datetime, timedelta

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.core.paginator import Paginator

from core.decorators import login_required, session_expired
from services.api_client import APIClient, JWTExpired


@login_required
def device_list(request, project_id):
    api = APIClient(request.COOKIES.get("access_token"))
    try:
        response = api.get_devices(project_id)
    except JWTExpired:
        return _tornar_al_login(request)
    devices = response.json()
    return render(request, "devices/device_list.html", {
        "project_id": project_id, "devices": devices,
    })


@login_required
def device_detail(request, project_id, device_id):
    api = APIClient(request.COOKIES.get("access_token"))
    try:
        device = api.get_device_detail(project_id, device_id).json()
        projecte = api.get_project_detail(project_id).json()
    except JWTExpired:
        return _tornar_al_login(request)
    return render(request, "devices/device_detail.html", {
        "project_id": project_id, "device_id": device_id,
        "project": projecte, "device": device,
    })


class DatesInvalides(ValueError):
    pass


class DadesAPIInvalides(ValueError):
    pass


def limits_dates(data_inici=None, data_final=None):
    def llegir(valor):
        if valor is None or valor == "":
            return None
        if not isinstance(valor, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", valor):
            raise DatesInvalides("Les dates han de tenir el format AAAA-MM-DD.")
        try:
            return datetime.strptime(valor, "%Y-%m-%d")
        except ValueError as exc:
            raise DatesInvalides("La data indicada no és vàlida.") from exc

    inici = llegir(data_inici)
    final = llegir(data_final)
    if inici is not None and final is not None and inici > final:
        raise DatesInvalides("La data inicial no pot ser posterior a la final.")
    try:
        fi_exclusiu = final + timedelta(days=1) if final is not None else None
    except OverflowError as exc:
        raise DatesInvalides("La data final és fora del rang admès.") from exc
    return inici, fi_exclusiu


def _data_lectura(text):
    for format_data in ("%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M:%S.%f"):
        try:
            return datetime.strptime(text.strip(), format_data)
        except ValueError:
            pass
    raise ValueError("Data de lectura no vàlida")


def parsejar_csv_dades(dades, data_inici=None, data_fi=None):
    if not isinstance(dades, list):
        raise DadesAPIInvalides("L'API no ha retornat una llista de dades.")
    resultat = []
    for bloc in dades:
        if isinstance(bloc, dict):
            csv_data = bloc.get("dada")
        elif isinstance(bloc, str):
            csv_data = bloc
        else:
            raise DadesAPIInvalides("L'API ha retornat un bloc no reconegut.")
        if csv_data is None or csv_data == "":
            continue
        if not isinstance(csv_data, str):
            raise DadesAPIInvalides("El contingut del bloc no és text.")
        #!!!Cada missatge pot contenir lectures de dies diferents.
        for row in csv.reader(io.StringIO(csv_data), delimiter=";"):
            if len(row) < 4:
                continue
            try:
                data = _data_lectura(row[2])
                valor = float(row[3].strip().replace(",", "."))
            except ValueError:
                continue
            if not math.isfinite(valor):
                continue
            if data_inici is not None and data < data_inici:
                continue
            if data_fi is not None and data >= data_fi:
                continue
            resultat.append({
                "magnitud": row[1].strip(), "data": data, "valor": valor,
                "camps_csv": row,
            })
    resultat.sort(key=lambda lectura: lectura["data"])
    return resultat


def _obtenir_lectures(request, project_id, device_id):
    inici, fi = limits_dates(request.GET.get("data_inici"), request.GET.get("data_final"))
    api = APIClient(request.COOKIES.get("access_token"))
    response = api.get_dades(project_id=project_id, device_id=device_id)
    if response.status_code != 200:
        raise DadesAPIInvalides("No s'han pogut obtenir les dades de l'API.")
    try:
        dades = response.json()
    except ValueError as exc:
        raise DadesAPIInvalides("L'API no ha retornat un JSON vàlid.") from exc
    try:
        return parsejar_csv_dades(dades, inici, fi)
    except csv.Error as exc:
        raise DadesAPIInvalides("El contingut CSV retornat per l'API no es pot llegir.") from exc


def _tornar_al_login(request):
    return session_expired(request)


def _error_text(exc, status):
    return HttpResponse(str(exc), status=status, content_type="text/plain; charset=utf-8")


@login_required
def dades_dispositiu(request, project_id, device_id):
    magnitud = request.GET.get("magnitud")
    try:
        dades = _obtenir_lectures(request, project_id, device_id)
    except DatesInvalides as exc:
        return _error_text(exc, 400)
    except JWTExpired:
        return _tornar_al_login(request)
    except DadesAPIInvalides as exc:
        return _error_text(exc, 502)
    dades_filtrades = [d for d in dades if d["magnitud"] == magnitud]
    paginator = Paginator(dades_filtrades, 10)
    page_obj = paginator.get_page(request.GET.get("page", 1))
    return render(request, "devices/partials/taula_dades.html", {
        "page_obj": page_obj, "magnitud": magnitud,
        "project_id": project_id, "device_id": device_id,
        "data_inici": request.GET.get("data_inici"),
        "data_final": request.GET.get("data_final"),
    })


@login_required
def dades_dispositiu_grafica(request, project_id, device_id):
    magnitud = request.GET.get("magnitud")
    try:
        dades = _obtenir_lectures(request, project_id, device_id)
    except DatesInvalides as exc:
        return JsonResponse({"error": str(exc), "labels": [], "values": []}, status=400)
    except JWTExpired:
        return _tornar_al_login(request)
    except DadesAPIInvalides as exc:
        return JsonResponse({"error": str(exc), "labels": [], "values": []}, status=502)
    dades_filtrades = [d for d in dades if d["magnitud"] == magnitud]
    return JsonResponse({
        "labels": [d["data"].strftime("%Y-%m-%d %H:%M:%S") for d in dades_filtrades],
        "values": [d["valor"] for d in dades_filtrades],
    })


@login_required
def descarregar_csv_raw(request, project_id, device_id):
    try:
        dades = _obtenir_lectures(request, project_id, device_id)
    except DatesInvalides as exc:
        return _error_text(exc, 400)
    except JWTExpired:
        return _tornar_al_login(request)
    except DadesAPIInvalides as exc:
        return _error_text(exc, 502)
    output = io.StringIO(newline="")
    writer = csv.writer(output, delimiter=";", lineterminator="\n")
    for lectura in dades:
        writer.writerow(lectura["camps_csv"])
    response = HttpResponse(output.getvalue(), content_type="text/csv; charset=utf-8")
    inici = request.GET.get("data_inici") or "inici"
    fi = request.GET.get("data_final") or "final"
    response["Content-Disposition"] = (
        f'attachment; filename="device_{device_id}_{inici}_{fi}_raw.csv"'
    )
    return response
