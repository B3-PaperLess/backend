from django.urls import path
from . import views

urlpatterns = [
    path('get-factures-siret', views.get_factures_with_siret),
    path('user', views.userAPI.as_view()),
    path('facture', views.factureAPI.as_view()),
]