from django.http import HttpResponse, HttpRequest, HttpResponseBadRequest, JsonResponse
from .models import Facture, User, Entreprise
from .serializers import UserSerializer
from django.core import serializers
from django.shortcuts import render
from django.views import View
import json
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
        params = get_parameters(request)
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
        params = get_parameters(request)

        error = check_required_parameters(params, ['nom', 'prenom', 'email', 'num_tel', 'password', 'siret', 'raison_social', 'ville', 'adresse'])
        if error is not None: return error

        nom = params["nom"]
        prenom = params["prenom"]
        email = params["email"]
        num_tel = params["num_tel"]
        password = params["password"]
        
        siret = params["siret"]
        raison_social=params['raison_social']
        ville=params['ville']
        adresse=params['adresse']


        entreprise = Entreprise.objects.create(
            siret=siret,
            nom=raison_social,
            adresse=adresse,
            ville=ville
        )

        user = User.objects.create(
            nom=nom,
            prenom=prenom,
            email=email,
            num_tel=num_tel,
            password=password,
            is_admin=True,
            entreprise=entreprise
        )

        return HttpResponse(True)

    def delete(self,request):
        params = get_parameters(request)
        siret = params["id"]
        error = check_required_parameters(params, ['id'])
        if error is not None: return error

        entreprise = Entreprise.objects.get(id=siret)
        return HttpResponse(entreprise.delete())

class userAPI(View):
    def get(self, request):
        params = get_parameters(request)
        user_id = params["id"]
        error = check_required_parameters(params, ['id'])
        if error is not None: return error

        user = User.objects.get(id=user_id)
        return HttpResponse(user)


    def post(self, request):

        return HttpResponse(request)


    def put(self, request):
        params = get_parameters(request)
        
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
        params = get_parameters(request)
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
        params = get_parameters(request)
        location, state, user_id = params["location"], params["state"], params["id"]
        error = check_required_parameters(params, ['user_id', 'location', 'state'])
        if error is not None: return error

        user = User.objects.get(id=user_id)
        facture = Facture.objects.create(user=user, location=location, state=state)

        return HttpResponse(facture)

    def put(self, request):
        params = get_parameters(request)
        state, facture_id = params["state"], params["id"]
        error = check_required_parameters(params, ['id'])
        if error is not None: return error

        facture = Facture.objects.get(id=facture_id)

        if state is not None:
            facture.state = state

        facture.save()
        return HttpResponse(facture)

    def delete(self,request):
        params = get_parameters(request)
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


def connect(request):
    params = get_parameters(request)
    error = check_required_parameters(params, ["email", "password"])
    if error is not None: return error
    
    email=params["email"]
    password=params["password"]

    try:
        user = User.objects.get(
                email=email,
                password=password
        )
        serializer = UserSerializer(user)
        user = serializer.data
    except User.DoesNotExist:
        return HttpResponseBadRequest('Identification Impossible')
    
    token = jwt.encode({"token":email}, os.getenv("TOKEN_KEY"), algorithm="HS256")
    return JsonResponse({'token':token, 'user':user}, safe=False)


def sign_up(request : HttpRequest):
    return HttpResponse("Not implemented !")


def get_GET_parameters(request, parameters, default_value=None) -> dict:
    ret = {}
    for parameter in parameters:
        ret[parameter] = request.GET.get(parameter, default_value)
    return ret

def get_parameters(request) -> dict :
    return json.loads(request.body.decode('utf-8'))

def check_required_parameters(parameters:dict, required):
    error = None
    for key in required:
        if parameters.get(key) is None:
            error = HttpResponseBadRequest("parameter '" + key + "' is required")
            break
    return error


def token_middleware(get_response):

    not_authenticated_paths = ["paperless/connect", "paperless/signup"]

    def middleware(request):
        path = request.path
        
        found=False
        for not_auth_path in not_authenticated_paths:
            if not_auth_path in path:
                found=True
                break
        
        if not found:
            token = request.COOKIES.get('token')
            if token is None:
                return HttpResponseBadRequest("Missing token")
            email = jwt.decode(token, os.getenv("TOKEN_KEY"), algorithms=["HS256"])["email"]
            if not User.objects.filter(email=email).exists():
                return HttpResponseBadRequest("Bad token")

        response = get_response(request)
        return response

    return middleware