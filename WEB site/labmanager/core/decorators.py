from functools import wraps

from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from services.api_client import APIError, JWTExpired


def is_ajax(request):
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


def session_expired(request):
    if is_ajax(request):
        response = JsonResponse({
            "error": "La sessió ha caducat. Torna a iniciar sessió.",
            "login_url": reverse("login"),
        }, status=401)
    else:
        response = redirect("login")
    response.delete_cookie("access_token")
    return response


def login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.COOKIES.get("access_token"):
            return session_expired(request)
        try:
            return view_func(request, *args, **kwargs)
        except JWTExpired:
            return session_expired(request)
        except APIError as exc:
            if is_ajax(request):
                return JsonResponse({"error": str(exc)}, status=exc.status_code)
            return render(request, "core/api_error.html", {
                "error": str(exc),
            }, status=exc.status_code)
    return wrapper
