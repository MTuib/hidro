"""
URL configuration for labmanager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

app_name = "devices"

urlpatterns = [
    path("project/<int:project_id>/", views.device_list, name="device_list"),
    path("project/<int:project_id>/<int:device_id>/", views.device_detail, name="device_detail"),
    path("project/<int:project_id>/<int:device_id>/dades/", views.dades_dispositiu, name="dades_dispositiu"),
    path("project/<int:project_id>/<int:device_id>/grafica/", views.dades_dispositiu_grafica, name="dades_dispositiu_grafica"),
    path("project/<int:project_id>/<int:device_id>/csv-raw/", views.descarregar_csv_raw, name="descarregar_csv_raw"),
]
