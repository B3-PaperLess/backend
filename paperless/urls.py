from django.urls import path
from . import views

urlpatterns = [
    path('get-factures-siret', views.get_factures_with_siret),
    path('get-facture', views.get_facture),
    path('delete-facture', views.delete_facture),
    path('update-facture', views.update_facture),
    path('create-facture', views.create_facture),
    path('get-factures', views.get_factures),
    path('get-user', views.get_user),
    path('delete-user', views.delete_user),
    path('update-user', views.update_user),
    path('create-user', views.create_user),
]