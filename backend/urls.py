from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls), # à supprimer par la suite surement comme tout les modules admins
    path('paperless/', include('paperless.urls'))
]
