from django.http import HttpResponse, HttpRequest, HttpResponseBadRequest

from .models import Facture, User

def get_factures_with_siret(request : HttpRequest):
    siret = request.GET.get("siret",None)
    if siret == None:
        return HttpResponseBadRequest("parameter siret not found")

    factures = Facture.objects.filter(user=siret)
    return HttpResponse(factures)

def get_facture(request : HttpRequest):
    id = request.GET.get("id", None)
    if id == None:
        return HttpResponseBadRequest("parameter ID not found")

    facture = Facture.objects.get(id=id)
    return HttpResponse(facture)

def get_factures():
    factures = Facture.objects.all()
    return HttpResponse(factures)

def update_facture(request : HttpRequest):
    id = request.GET.get("id", None)
    state = request.GET.get("state", None)
    if id == None:
        return HttpResponseBadRequest("parameter ID not found")

    facture = Facture.objects.get(id=id)

    if state != None:
        facture.state = state

    facture.save()
    return HttpResponse(facture)

def delete_facture(request : HttpRequest):
    id = request.GET.get("id", None)
    if id == None:
        return HttpResponseBadRequest("parameter ID not found")

    facture = Facture.objects.get(id=id)
    return HttpResponse(facture.delete())

def create_facture(request : HttpRequest):
    location = request.GET.get("location", None)
    state=request.GET.get("state", "EN_COURS")
    siret=request.GET.get("siret", None)

    if siret == None:
        return HttpResponseBadRequest("parameter siret not found")
    if location == None:
        return HttpResponseBadRequest("parameter location not found")

    user = User.objects.get(siret=siret)
    facture = Facture.objects.create(user=user, location=location, state=state)

    return HttpResponse(facture)


def get_user(request : HttpRequest):
    siret = request.GET.get("siret", None)

    if siret == None:
        return HttpResponseBadRequest("parameter Siret not found")

    user = User.objects.get(siret=siret)
    return HttpResponse(user)

def delete_user(request : HttpRequest):
    siret = request.GET.get("siret", None)

    if siret == None:
        return HttpResponseBadRequest("parameter Siret not found")

    user = User.objects.get(siret=siret)
    return HttpResponse(user.delete())

def update_user(request : HttpRequest):
    nom = request.GET.get("nom", None)
    password = request.GET.get("password", None)
    siret = request.GET.get("siret", None)

    if siret == None:
        return HttpResponseBadRequest("parameter Siret not found")

    user = User.objects.get(siret=siret)

    if nom != None:
        user.nom = nom
    if password != None:
        user.password = password

    user.save()

    return HttpResponse(user)

def create_user(request : HttpRequest):
    siret = request.GET.get("siret", None)
    nom = request.GET.get("nom", None)
    password = request.GET.get("password", None)

    if siret == None:
        return HttpResponseBadRequest("parameter Siret not found")
    if nom == None:
        return HttpResponseBadRequest("parameter Nom not found")
    if password == None:
        return HttpResponseBadRequest("parameter Password not found")

    user = User.objects.create(siret=siret, nom=nom, password=password)

    return HttpResponse(user)