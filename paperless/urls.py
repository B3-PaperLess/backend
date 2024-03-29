from django.http import HttpResponse
from django.urls import path
from . import views

urlpatterns = [
    path('connect', views.connect, name='connect'),
    path('signup', views.sign_up, name='signup'),
    path('entreprise-factures', views.get_factures_entreprise),
    path('entreprise-users', views.entreprise_users),
    path('transfer-admin', views.transfer_admin),
    path('user', views.userAPI.as_view()),
    path('me', views.me),
    path('facture', views.factureAPI.as_view()),
    path('entreprise', views.entrepriseAPI.as_view()),
    path('password-change', views.password_change),
]