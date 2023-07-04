from django.http import HttpResponse, HttpRequest

from .models import Facture

def get_facture(request : HttpRequest):
    id = request.GET.get("id", None)
    if id == None:
        return HttpResponse("parameter ID not found")

    facture = Facture.objects.get(id=id)
    return HttpResponse(facture)

def get_factures():
    factures = Facture.objects.all()
    return HttpResponse(factures)

def update_facture(request : HttpRequest):
    id = request.GET.get("id", None)
    state = request.GET.get("state", None)
    if id == None:
        return HttpResponse("parameter ID not found")

    facture = Facture.objects.get(id=id)

    if state != None:
        facture.state = state

    facture.save()
    return HttpResponse(facture)

def delete_facture(request : HttpRequest):
    id = request.GET.get("id", None)
    if id == None:
        return HttpResponse("parameter ID not found")

    facture = Facture.objects.get(id=id)
    return HttpResponse(facture.delete())

def create_facture(request : HttpRequest):
    location = request.GET.get("location", None)
    state=request.GET.get("state", "EN_COURS")
    id = request.GET.get('id', None)

    if location == None:
        return HttpResponse("parameter location not found")

    facture = Facture.objects.create()

    facture.location = location
    facture.state = state
    facture.save()

    return HttpResponse(facture)


def get_user():
    pass

def delete_user():
    pass

def update_user():
    pass

def create_user():
    pass