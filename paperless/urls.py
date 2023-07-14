from django.http import HttpResponse
from django.urls import path
from . import views

urlpatterns = [
    path('connect', views.connect),
    path('signup', views.sign_up),
    path('factures-user', views.get_factures_with_user),
    path('user', views.userAPI.as_view()),
    path('facture', views.factureAPI.as_view()),
    path('entreprise', views.entrepriseAPI.as_view()),
    path('test', views.testFile)
]