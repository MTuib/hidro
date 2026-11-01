from django.shortcuts import render
from core.decorators import login_required
from services.api_client import APIClient
from django.shortcuts import redirect
from services.api_client import JWTExpired

# Create your views here.

@login_required
def project_list(request):
    token = request.COOKIES.get("access_token")
    api = APIClient(token)
    try:
        response = api.get_projects()
    except JWTExpired:
        response = redirect("login")
        response.delete_cookie("access_token")
        return response


    
    projects = response.json()
    return render(request, "projects/project_list.html", {"projects": projects})
