import uuid

from django.http import HttpResponse, HttpRequest, HttpResponseBadRequest, JsonResponse
from django.core.files.storage import default_storage
from .serializers import UserSerializer, EntrepriseSerializer, FactureSerializer
from django.views import View
import json
import jwt
import os
from .models import Facture, User, Entreprise

class entrepriseAPI(View):
    def get(self, request):
        params = request.GET
        error = check_required_parameters(params, ['id'])
        if error is not None: return error

        siret = params["id"]
        entreprise = Entreprise.objects.get(siret=siret)
        entreprise_seria = EntrepriseSerializer(entreprise)
        entreprise_data = entreprise_seria.data

        admin = User.objects.get(entreprise=params['id'], is_admin=True)
        admin = UserSerializer(admin)
        admin = admin.data

        return JsonResponse({'entreprise': entreprise_data, 'admin': admin}, safe=False)

    def put(self, request):
        params = get_parameters(request)
        siret, nom, adresse, ville, valide = params["id"], params["nom"], params["adresse"], params["ville"], params[
            "valide"]
        error = check_required_parameters(params, ['id'])
        if error is not None: return error

        entreprise = Entreprise.objects.get(id=siret)

        if nom is not None:
            entreprise.nom = nom
        if adresse is not None:
            entreprise.adresse = adresse
        if ville is not None:
            entreprise.ville = ville
        if valide is not None:
            entreprise.valide = valide

        entreprise.save()
        seria_entreprise = EntrepriseSerializer(entreprise).data
        return JsonResponse({"entreprise" : seria_entreprise}, safe=False)

    def post(self, request):
        return HttpResponse(True)

    def delete(self, request):
        params = get_parameters(request)
        siret = params["id"]
        error = check_required_parameters(params, ['id'])
        if error is not None: return error

        entreprise = Entreprise.objects.get(id=siret)
        entreprise.delete()
        return HttpResponse(True)


def get_user_from_request(request):
    admin_email = decode_token(request.COOKIES.get('token'))
    admin_users = User.objects.filter(email=admin_email)
    if len(admin_users) == 0:
        return HttpResponseBadRequest("Incohérence du token avec la base de données")

    return admin_users[0]


def get_entreprise_from_request(request):
    admin_email = decode_token(request.COOKIES.get('token'))
    admin_users = User.objects.filter(email=admin_email)
    if len(admin_users) == 0:
        return HttpResponseBadRequest("Incohérence du token avec la base de données")

    return admin_users[0].entreprise

class userAPI(View):
    def get(self, request):
        params = get_parameters(request)
        user_id = params["id"]
        error = check_required_parameters(params, ['id'])
        if error is not None: return error

        user = User.objects.get(id=user_id)
        user_seria = UserSerializer(user).data
        return JsonResponse({"user": user_seria}, safe=False)

    def post(self, request):
        params = get_parameters(request)

        siret = get_entreprise_from_request(request).siret

        error = check_required_parameters(params,
                                          ['nom', 'prenom', 'email', 'num_tel', 'password'])
        if error is not None: return error

        nom = params["nom"]
        prenom = params["prenom"]
        email = params["email"]
        num_tel = params["num_tel"]
        password = params["password"]

        entreprise = Entreprise.objects.get(siret=siret)

        if User.objects.filter(email=email).exists():
            return HttpResponseBadRequest("Un utilisateur avec cette email existe déjà")

        user = User.objects.create(
            nom=nom,
            prenom=prenom,
            email=email,
            num_tel=num_tel,
            password=password,
            is_admin=False,
            entreprise=entreprise
        )

        user_seria = UserSerializer(user).data
        return JsonResponse({"user": user_seria}, safe=False)

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
            user.email = email

        user.save()

        user_seria = UserSerializer(user).data
        return JsonResponse({"user": user_seria}, safe=False)

    def delete(self, request):
        params = request.GET
        error = check_required_parameters(params, ['email'])
        if error is not None: return error

        user = User.objects.get(email=params['email'])

        if user.is_admin:
            return HttpResponseBadRequest("L'utilisateur est un admin, impossible de supprimer")

        user.delete()
        return HttpResponse(True)

def me(request):
    user = get_user_from_request(request)
    user = UserSerializer(user)
    return JsonResponse(user.data, safe=False)

class factureAPI(View):
    def get(self, request):
        params = get_GET_parameters(request, ["id"])
        facture_id = params["id"]
        error = check_required_parameters(params, ['id'])
        if error is not None: return error

        facture = Facture.objects.get(id=facture_id)

        facture_seria = FactureSerializer(facture).data
        return JsonResponse({"facture": facture_seria}, safe=False)

    def post(self, request):
        user = get_user_from_request(request)
        file = request.FILES.get("file")
        state = request.POST.get("state")

        if state is None:
            state = "NEW"

        print(request.FILES)
        location = str(uuid.uuid4())
        default_storage.save("storage/factures/"+location, file)
        facture = Facture.objects.create(user=user, location="storage/factures/"+location, state=state)


        facture_seria = FactureSerializer(facture).data
        return JsonResponse({"facture": facture_seria}, safe=False)


    def put(self, request):
        params = get_parameters(request)
        state, facture_id = params["state"], params["id"]
        error = check_required_parameters(params, ['id'])
        if error is not None: return error

        facture = Facture.objects.get(id=facture_id)

        if state is not None:
            facture.state = state

        facture.save()

        facture_seria = FactureSerializer(facture).data
        return JsonResponse({"facture": facture_seria}, safe=False)


    def delete(self, request):
        params = get_GET_parameters(request, ["id"])
        facture_id = params["id"]
        error = check_required_parameters(params, ["id"])
        if error is not None: return error

        facture = Facture.objects.get(id=facture_id)

        if default_storage.exists(facture.location):
            default_storage.delete(facture.location)

        facture.delete()
        return HttpResponse(True)


def get_factures_with_user(request: HttpRequest):
    params = get_GET_parameters(request, ["id"])
    user_id = params["id"]
    error = check_required_parameters(params, ["id"])
    if error is not None: return error

    factures_query_set = Facture.objects.filter(user=user_id)
    factures = []

    for facture in factures_query_set:
        factures.append(FactureSerializer(facture).data)
    return JsonResponse({"factures": factures}, safe=False)

def connect(request):
    params = get_parameters(request)
    error = check_required_parameters(params, ["email", "password"])
    if error is not None: return error

    email = params["email"]
    password = params["password"]

    try:
        user = User.objects.get(
            email=email,
            password=password
        )
        serializer = UserSerializer(user)
        user = serializer.data

    except User.DoesNotExist:
        return HttpResponseBadRequest('Email ou mot de passe invalide')

    token = jwt.encode({"token": email}, os.getenv("TOKEN_KEY"), algorithm="HS256")
    return JsonResponse({'token': token, 'user': user}, safe=False)


def sign_up(request: HttpRequest):
    params = get_parameters(request)

    error = check_required_parameters(params,
                                      ['nom', 'prenom', 'email', 'num_tel', 'password', 'siret', 'raison_social',
                                       'ville', 'adresse'])
    if error is not None: return error

    nom = params["nom"]
    prenom = params["prenom"]
    email = params["email"]
    num_tel = params["num_tel"]
    password = params["password"]

    siret = params["siret"]
    raison_social = params['raison_social']
    ville = params['ville']
    adresse = params['adresse']

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

    return HttpResponse(user)


def get_GET_parameters(request, parameters, default_value=None) -> dict:
    ret = {}
    for parameter in parameters:
        ret[parameter] = request.GET.get(parameter, default_value)
    return ret


def get_parameters(request) -> dict:
    return json.loads(request.body.decode('utf-8'))


def check_required_parameters(parameters: dict, required):
    error = None
    for key in required:
        if parameters.get(key) is None:
            error = HttpResponseBadRequest("parameter '" + key + "' is required")
            break
    return error


def token_middleware(get_response):
    not_authenticated_paths = ["paperless/connect", "paperless/signup", "admin"]

    def middleware(request):
        path = request.path

        found = False
        for not_auth_path in not_authenticated_paths:
            if not_auth_path in path:
                found = True
                break

        if not found:
            token = request.COOKIES.get('token')
            if token is None:
                return HttpResponseBadRequest("Missing token")
            email = decode_token(token)
            if not len(User.objects.filter(email=email)) != 0:
                return HttpResponseBadRequest("Bad token")

        response = get_response(request)
        return response

    return middleware

def entreprise_users(request):
    user = get_user_from_request(request)
    if not user.is_admin:
        return HttpResponseBadRequest("L'utilisateur est un admin, impossible de supprimer")

    # entreprise = Entreprise.objects.get(siret=user.entreprise.siret)

    users = User.objects.filter(entreprise=user.entreprise)
    users = [UserSerializer(user).data for user in users]

    return JsonResponse({'users': users}, safe=False)


def transfer_admin(request):
    params = get_parameters(request)
    check_required_parameters(params, "id")

    id = params["id"]
    user = User.objects.get(id=id)
    admin_user = get_user_from_request(request)

    if user.id == admin_user.id:
        return HttpResponseBadRequest("Vous ne pouvez pas vous transferer vous même le role d'admin")
    if not is_user_of_entreprise(user, admin_user.entreprise):
        return HttpResponseBadRequest("Cet utilisateur n'appartient pas a la même entreprise que vous")
    if not admin_user.is_admin:
        return HttpResponseBadRequest("Vous n'êtes pas un admin")

    user.is_admin = True
    user.save()

    admin_user.is_admin = False
    admin_user.save()

    return HttpResponse("transfert d'admin effectué")


def is_user_of_entreprise(user, entreprise):
    return user.entreprise.siret == entreprise.siret


def decode_token(token):
    return jwt.decode(token, os.getenv("TOKEN_KEY"), algorithms=["HS256"])["token"]