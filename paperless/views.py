from django.http import HttpResponse, HttpRequest, HttpResponseBadRequest
from django.views import View

from .models import Facture, User, Entreprise

class entrepriseAPI(View):
    def get(self, request):
        params = get_GET_parameters(request, ["id"])
        siret = params["id"]
        error = check_required_parameters(params, ['id'])
        if error is not None: return error

        entreprise = Entreprise.objects.get(siret=siret)
        return HttpResponse(entreprise)

    def put(self, request):
        params = get_POST_parameters(request, ["id","nom","adresse","ville"])
        siret, nom, adresse, ville = params["id"],params["nom"],params["adresse"],params["ville"]
        error = check_required_parameters(params, ['id'])
        if error is not None: return error

        entreprise = Entreprise.objects.get(id=siret)

        if nom is not None:
            entreprise.nom = nom
        if adresse is not None:
            entreprise.adresse = adresse
        if ville is not None:
            entreprise.ville=ville

        entreprise.save()

        return HttpResponse(entreprise)

    def post(self, request):
        params = get_POST_parameters(request, ["id"])
        siret, nom, adresse, ville = \
            params["id"], \
            params["nom"], \
            params["adresse"], \
            params["ville"]
        error = check_required_parameters(params, ['id', 'nom', 'adresse', 'ville'])
        if error is not None: return error

        entreprise = Entreprise.objects.create(
            siret=siret,
            nom=nom,
            adresse=adresse,
            ville=ville
        )

        return HttpResponse(entreprise)

    def delete(self,request):
        params = get_POST_parameters(request, ["id"])
        siret = params["id"]
        error = check_required_parameters(params, ['id'])
        if error is not None: return error

        entreprise = Entreprise.objects.get(id=siret)
        return HttpResponse(entreprise.delete())

class userAPI(View):
    def get(self, request):
        params = get_GET_parameters(request, ["id"])
        user_id = params["id"]
        error = check_required_parameters(params, ['id'])
        if error is not None: return error

        user = User.objects.get(id=user_id)
        return HttpResponse(user)


    def post(self, request):
        params = get_POST_parameters(request, ["id", "nom", "password", "email", "is_admin", "entreprise_id"])
        user_id, email, nom, password, is_admin, entreprise_id = \
            params["id"], \
            params["email"], \
            params["nom"], \
            params["password"], \
            params["is_admin"], \
            params["entreprise_id"]
        error = check_required_parameters(params, ['email', 'nom', 'password', 'entreprise_id'])
        if error is not None: return error

        entreprise = Entreprise.objects.get(entreprise_id)

        user = User.objects.create(
            email=email,
            nom=nom,
            password=password,
            entreprise=entreprise)

        #Params optionnels
        if is_admin is not None:
            user.is_admin = is_admin
        user.save()

        return HttpResponse(user)


    def put(self, request):
        params = get_POST_parameters(request, ["id","nom","password","email"])
        user_id, nom, password, email = params["id"],params["nom"],params["password"],params["email"]
        error = check_required_parameters(params, ['id'])
        if error is not None: return error

        user = User.objects.get(id=user_id)

        if nom is not None:
            user.nom = nom
        if password is not None:
            user.password = password
        if email is not None:
            user.email=email

        user.save()

        return HttpResponse(user)


    def delete(self,request):
        params = get_POST_parameters(request, ["id"])
        user_id = params["id"]
        error = check_required_parameters(params, ['id'])
        if error is not None: return error

        user = User.objects.get(id=user_id)
        return HttpResponse(user.delete())


class factureAPI(View):
    def get(self, request):
        params = get_GET_parameters(request, ["id"])
        facture_id = params["id"]
        error = check_required_parameters(params, ['id'])
        if error is not None: return error

        facture = Facture.objects.get(id=facture_id)
        return HttpResponse(facture)

    def post(self, request):
        params = get_POST_parameters(request, ["location", "state","user_id"])
        location, state, user_id = params["location"], params["state"], params["id"]
        error = check_required_parameters(params, ['user_id', 'location', 'state'])
        if error is not None: return error

        user = User.objects.get(id=user_id)
        facture = Facture.objects.create(user=user, location=location, state=state)

        return HttpResponse(facture)

    def put(self, request):
        params = get_POST_parameters(request, ["id", "state"])
        state, facture_id = params["state"], params["id"]
        error = check_required_parameters(params, ['id'])
        if error is not None: return error

        facture = Facture.objects.get(id=facture_id)

        if state is not None:
            facture.state = state

        facture.save()
        return HttpResponse(facture)

    def delete(self,request):
        params = get_POST_parameters(request, ["id"])
        facture_id = params["id"]
        error = check_required_parameters(params, ["id"])
        if error is not None: return error

        facture = Facture.objects.get(id=facture_id)
        return HttpResponse(facture.delete())

def get_factures_with_user(request : HttpRequest):
    params = get_POST_parameters(request, ["id"])
    user_id = params["id"]
    error = check_required_parameters(params, ["id"])
    if error is not None: return error

    factures = Facture.objects.filter(user=user_id)
    return HttpResponse(factures)


def get_GET_parameters(request, parameters) -> dict:
    ret = {}
    for parameter in parameters:
        ret[parameter] = request.GET.get(parameter, None)
    return ret

def get_POST_parameters(request, parameters) -> dict :
    ret = {}
    for parameter in parameters:
        ret[parameter] = request.POST.get(parameter, None)
    return ret

def check_required_parameters(parameters:dict, required):
    error = None
    for key in required:
        if parameters.get(key) is None:
            error = HttpResponseBadRequest("parameter '" + key + "' is required")
            break
    return error