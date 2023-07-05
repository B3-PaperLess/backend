from django.http import HttpResponse, HttpRequest, HttpResponseBadRequest
from django.views import View

from .models import Facture, User, Entreprise

class entrepriseAPI(View):
    def get(self, request):
        id = request.GET.get("id", None)

        if id == None

class userAPI(View):
    def get(self, request):
        siret = request.GET.get("siret", None)

        if siret == None:
            return HttpResponseBadRequest("parameter 'siret' not found")

        user = User.objects.get(siret=siret)
        return HttpResponse(user)


    def post(self, request):
        siret = request.GET.get("siret", None)
        entreprise_id = request.GET.get("entreprise_id", None)
        nom = request.GET.get("nom", None)
        password = request.GET.get("password", None)

        if siret == None:
            return HttpResponseBadRequest("parameter 'siret' not found")
        if entreprise_id == None:
            return HttpResponseBadRequest("parameter 'entreprise_id' not found")
        if nom == None:
            return HttpResponseBadRequest("parameter 'nom' not found")
        if password == None:
            return HttpResponseBadRequest("parameter 'password' not found")

        entreprise = Entreprise.objects.get(entreprise_id)

        user = User.objects.create(
            siret=siret, 
            nom=nom, 
            password=password, 
            entreprise=entreprise)

        return HttpResponse(user)


    def put(self, request):
        nom = request.GET.get("nom", None)
        password = request.GET.get("password", None)
        siret = request.GET.get("siret", None)

        if siret == None:
            return HttpResponseBadRequest("parameter 'siret' not found")

        user = User.objects.get(siret=siret)

        if nom != None:
            user.nom = nom
        if password != None:
            user.password = password

        user.save()

        return HttpResponse(user)


    def delete(self,request):
        siret = request.GET.get("siret", None)

        if siret == None:
            return HttpResponseBadRequest("parameter 'siret' not found")

        user = User.objects.get(siret=siret)
        return HttpResponse(user.delete())


class factureAPI(View):
    def get(self, request):
        id = request.GET.get("id", None)
        if id == None:
            return HttpResponseBadRequest("parameter 'id' not found")

        facture = Facture.objects.get(id=id)
        return HttpResponse(facture)
    
    def post(self, request):
        location = request.GET.get("location", None)
        state=request.GET.get("state", "EN_COURS")
        siret=request.GET.get("siret", None)

        if siret == None:
            return HttpResponseBadRequest("parameter 'siret' not found")
        if location == None:
            return HttpResponseBadRequest("parameter 'location' not found")

        user = User.objects.get(siret=siret)
        facture = Facture.objects.create(user=user, location=location, state=state)

        return HttpResponse(facture)

    def put(self, request):
        id = request.GET.get("id", None)
        state = request.GET.get("state", None)
        if id == None:
            return HttpResponseBadRequest("parameter 'id' not found")

        facture = Facture.objects.get(id=id)

        if state != None:
            facture.state = state

        facture.save()
        return HttpResponse(facture)

    def delete(self,request):
        id = request.GET.get("id", None)
        if id == None:
            return HttpResponseBadRequest("parameter 'id' not found")

        facture = Facture.objects.get(id=id)
        return HttpResponse(facture.delete())

def get_factures_with_siret(request : HttpRequest):
    siret = request.GET.get("siret",None)
    if siret == None:
        return HttpResponseBadRequest("parameter 'siret' not found")

    factures = Facture.objects.filter(user=siret)
    return HttpResponse(factures)


def _requiredParameters(parameters):
    for parameter in parameters:
        pass
    