import os
from django.http import HttpResponse, HttpRequest, HttpResponseBadRequest
from django.views import View
from django.shortcuts import render
import jwt
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
        params = get_POST_parameters(request, ["id", 'nom', 'adresse', 'ville'])
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
        required_params = ["password", "email", "entreprise_id"]
        optional_params = ["is_admin", "nom", "prenom", "num_tel"]
        all_params = required_params+optional_params

        params = get_POST_parameters(request, all_params)

        email = params["email"]
        nom = params["nom"]
        prenom = params["prenom"]
        num_tel = params["num_tel"]
        password = params["password"]
        is_admin = params["is_admin"]
        entreprise_id = params["entreprise_id"]

        error = check_required_parameters(params, required_params)
        if error is not None: return error

        entreprise = Entreprise.objects.get(entreprise_id)

        user = User.objects.create(
            email=email,
            password=password,
            entreprise=entreprise)

        #Params optionnels
        if is_admin is not None:
            user.is_admin = is_admin
        if nom is not None:
            user.nom = nom
        if num_tel is not None:
            user.num_tel = num_tel
        if prenom is not None:
            user.prenom = prenom

        user.save()

        return HttpResponse(user)


    def put(self, request):
        params = get_POST_parameters(request, ["id","nom", "prenom", "num_tel", "password","email"])
        
        user_id = params["id"],
        nom = params["nom"]
        prenom = params["prenom"]
        num_tel = params["num_tel"]
        password = params["password"]
        email = params["email"]
        
        error = check_required_parameters(params, ['id'])
        if error is not None: return error

        user = User.objects.get(id=user_id)

        if nom is not None:
            user.nom = nom
        if num_tel is not None:
            user.num_tel = num_tel
        if prenom is not None:
            user.prenom = prenom
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
    params = get_GET_parameters(request, ["id"])
    user_id = params["id"]
    error = check_required_parameters(params, ["id"])
    if error is not None: return error

    factures = Facture.objects.filter(user=user_id)
    return HttpResponse(factures)

def connect(request : HttpRequest):
    params = get_GET_parameters(request, ["email","password"])
    error = check_required_parameters(params, ["email", "password"])
    if error is not None: return error
    
    email=params["email"]
    password=params["password"]

    user = User.objects.get(
        email=email,
        password=password
    )

    res = HttpResponse(user)
    token = jwt.encode({"token":email}, os.getenv("TOKEN_KEY"), algorithm="HS256")
    res.set_cookie("token", token, httponly=True, secure=True)
    return res

def get_GET_parameters(request, parameters, default_value=None) -> dict:
    ret = {}
    for parameter in parameters:
        ret[parameter] = request.GET.get(parameter, default_value)
    return ret

def get_POST_parameters(request, parameters, default_value=None) -> dict :
    ret = {}
    for parameter in parameters:
        ret[parameter] = request.POST.get(parameter, default_value)
    return ret

def check_required_parameters(parameters:dict, required):
    error = None
    for key in required:
        if parameters.get(key) is None:
            error = HttpResponseBadRequest("parameter '" + key + "' is required")
            break
    return error