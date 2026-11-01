from django.conf import settings
from django.shortcuts import render, redirect

from services.api_client import APIClient, APIError


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        if not username or not password:
            return render(request, "core/login.html", {
                "error": "Introdueix l'usuari i la contrasenya.",
            }, status=400)
        try:
            data = APIClient().login(username, password)
        except APIError as exc:
            return render(request, "core/login.html", {
                "error": str(exc),
            }, status=exc.status_code)
        response = redirect("projects:project_list")
        response.set_cookie(
            "access_token", data["access_token"],
            httponly=True, samesite="Lax", secure=settings.JWT_COOKIE_SECURE,
        )
        return response
    return render(request, "core/login.html")


def logout_view(request):
    response = redirect("login")
    response.delete_cookie("access_token")
    return response
