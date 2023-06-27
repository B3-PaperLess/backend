from django.http import HttpResponse, HttpRequest

import paperless.models
from .models import Facture


def importer_facture(request):
    pass

def obtenir_facture(request : HttpRequest):
    id = request.GET.get("id", None)
    if id == None:
        print("SIRET ERROR")
        return HttpResponse(id)
        return HttpResponse(Facture.objects.all())
        return HttpResponse("erreur")

    facture = Facture.objects.get(id=id)
    return HttpResponse(facture)