import uuid
import requests
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import MultipleObjectsReturned
from django.http import HttpResponse, HttpRequest, HttpResponseBadRequest, JsonResponse
from django.core.files.storage import default_storage
from .serializers import UserSerializer, EntrepriseSerializer, FactureSerializer, FactureWithUserSerializer
from django.views import View
import json
import jwt
import os
from .models import Facture, User, Entreprise


# region API

# region API CRUD

class entrepriseAPI(View):
    def get(self, request):
        entreprise = get_entreprise_from_request(request)
        entreprise_seria = EntrepriseSerializer(entreprise)
        entreprise_data = entreprise_seria.data

        admin = User.objects.get(entreprise=entreprise, is_admin=True)
        admin = UserSerializer(admin)
        admin = admin.data

        return JsonResponse({'entreprise': entreprise_data, 'admin': admin}, safe=False)

    def put(self, request):
        params = get_parameters(request)
        siret, nom, adresse, ville = params["siret"], params["nom"], params["adresse"], params["ville"]
        error = check_required_parameters(params, ['siret'])
        if error is not None: return error

        try:
            entreprise = Entreprise.objects.get(siret=siret)
        except ObjectDoesNotExist:
            return HttpResponseBadRequest("Entreprise non trouvée")

        if nom is not None:
            entreprise.nom = nom
        if adresse is not None:
            entreprise.adresse = adresse
        if ville is not None:
            entreprise.ville = ville

        entreprise.is_updated = True

        entreprise.save()
        seria_entreprise = EntrepriseSerializer(entreprise).data
        return JsonResponse({"entreprise": seria_entreprise}, safe=False)

    def post(self, request):
        return HttpResponse(True)

    def delete(self, request):
        params = get_parameters(request)
        siret = params["id"]
        error = check_required_parameters(params, ['id'])
        if error is not None: return error

        try:
            entreprise = Entreprise.objects.get(id=siret)
        except ObjectDoesNotExist:
            return HttpResponseBadRequest("Entreprise non trouvée")

        entreprise.delete()
        return HttpResponse(True)


class userAPI(View):
    def get(self, request):
        params = get_parameters(request)
        user_id = params["id"]
        error = check_required_parameters(params, ['id'])
        if error is not None: return error

        try:
            user = User.objects.get(id=user_id)
        except ObjectDoesNotExist:
            return HttpResponseBadRequest("Utilisateur non trouvé")

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

        try:
            entreprise = Entreprise.objects.get(siret=siret)
        except ObjectDoesNotExist:
            return HttpResponseBadRequest("Entreprise non trouvée, SIRET invalide")

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
        error = check_required_parameters(params, ['nom', 'prenom', 'email', 'tel'])
        if error is not None: return error

        nom = params["nom"]
        prenom = params["prenom"]
        num_tel = params["tel"]
        email = params["email"]

        user = get_user_from_request(request)
        if user is None:
            return HttpResponseBadRequest("Utilisateur connecté non trouvé")

        if nom is not None:
            user.nom = nom
        if num_tel is not None:
            user.num_tel = num_tel
        if prenom is not None:
            user.prenom = prenom
        if email is not None:
            user.email = email

        user.save()

        user_seria = UserSerializer(user).data
        return JsonResponse({"user": user_seria}, safe=False)

    def delete(self, request):
        params = request.GET
        error = check_required_parameters(params, ['email'])
        if error is not None: return error

        connected_user = get_user_from_request(request)
        if connected_user is None:
            return HttpResponseBadRequest("Utilisateur connecté non trouvé")

        try:
            user = User.objects.get(email=params['email'])
        except ObjectDoesNotExist:
            return HttpResponseBadRequest("Utilisateur non trouvé, l'email est invalide")

        if connected_user.id == user.id:
            return HttpResponseBadRequest("Vous ne pouvez pas supprimer ce compte tant que vous y êtes connecté")

        if user.is_admin:
            return HttpResponseBadRequest("L'utilisateur est un admin, impossible de supprimer")

        user.delete()
        return HttpResponse(True)


class factureAPI(View):
    def get(self, request):
        params = get_GET_parameters(request, ["id"])
        facture_id = params["id"]
        error = check_required_parameters(params, ['id'])
        if error is not None: return error

        try:
            facture = Facture.objects.get(id=facture_id)
        except ObjectDoesNotExist:
            return HttpResponseBadRequest("Facture non trouvée")

        facture_seria = FactureSerializer(facture).data
        return JsonResponse({"facture": facture_seria}, safe=False)

    def post(self, request):
        user = get_user_from_request(request)
        if user is None:
            return HttpResponseBadRequest("Utilisateur connecté non trouvé")

        file = request.FILES['file']

        location = str(uuid.uuid4())

        # Sauvegarde du fichier de la facture et insertion en base de donnée
        default_storage.save("storage/factures/" + location, file)
        facture = Facture.objects.create(user=user, location="storage/factures/" + location, state="NEW",
                                         taille=file.size, nom=file.name.split('.')[0])

        # Envoi de la facture à chorus, on place le retour a True par défaut car aucun accès à la base école
        # ret = send_to_chorus(file)
        ret = True

        # Si tout s'est bien passé on passe l'état à envoyé, et on supprime la facture de notre bdd
        if ret:
            facture.state = "SENT"
            delete_facture_file(facture)
        else:
            return HttpResponseBadRequest(ret)

        facture_seria = FactureSerializer(facture).data
        return JsonResponse({"facture": facture_seria}, safe=False)

    def put(self, request):
        params = get_parameters(request)
        facture_id = params["id"]
        error = check_required_parameters(params, ['id'])
        if error is not None: return error

        try:
            facture = Facture.objects.get(id=facture_id)
        except ObjectDoesNotExist:
            return HttpResponseBadRequest("Facture non trouvée")

        facture.save()

        facture_seria = FactureSerializer(facture).data
        return JsonResponse({"facture": facture_seria}, safe=False)

    def delete(self, request):
        params = get_GET_parameters(request, ["id"])
        facture_id = params["id"]
        error = check_required_parameters(params, ["id"])
        if error is not None: return error

        try:
            facture = Facture.objects.get(id=facture_id)
        except ObjectDoesNotExist:
            return HttpResponseBadRequest("Facture non trouvée")

        # Suppression du fichier et de la ligne en BDD
        delete_facture_file(facture)
        facture.delete()

        return HttpResponse(True)


# endregion API CRUD

# region API functions

def me(request):
    user = get_user_from_request(request)
    if user is None:
        return HttpResponseBadRequest("Utilisateur connecté non trouvé")
    user = UserSerializer(user)
    return JsonResponse(user.data, safe=False)


def password_change(request):
    params = get_parameters(request)
    user = get_user_from_request(request)
    if user is None:
        return HttpResponseBadRequest("Utilisateur connecté non trouvé")

    error = check_required_parameters(params, ['passwordCurrent', 'passwordNew'])
    if error is not None: return error

    if user.password != params['passwordCurrent']:
        return HttpResponseBadRequest('Mauvais mot de passe')

    user.password = params['passwordNew']
    user.save()

    return JsonResponse({'response': True}, safe=False)


def get_factures_entreprise(request: HttpRequest):
    """ Obtenir les factures d'une entreprise
    """

    entreprise = get_entreprise_from_request(request)
    users_entreprise = User.objects.filter(entreprise=entreprise)
    factures = []
    for user in users_entreprise:
        factures_user = Facture.objects.filter(user=user)
        for facture in factures_user:
            factures.append(facture)
    factures = FactureWithUserSerializer(factures, many=True)
    return JsonResponse({"factures": factures.data}, safe=False)


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

    except ObjectDoesNotExist:
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
    serializer = UserSerializer(user)
    user = serializer.data

    return JsonResponse({'user': user}, safe=False)


def entreprise_users(request):
    """ Obtenir les utilisateurs d'une entreprise
    """
    user = get_user_from_request(request)
    if user is None:
        return HttpResponseBadRequest("Utilisateur connecté non trouvé")
    if not user.is_admin:
        return HttpResponseBadRequest("L'utilisateur est un admin, impossible de supprimer")

    # entreprise = Entreprise.objects.get(siret=user.entreprise.siret)

    users = User.objects.filter(entreprise=user.entreprise)
    users = [UserSerializer(user).data for user in users]

    return JsonResponse({'users': users}, safe=False)


def transfer_admin(request):
    """ Transferer le role d'admin de l'entreprise à un autre utilisateur de l'entreprise
    """
    params = get_parameters(request)
    check_required_parameters(params, "email")
    email = params["email"]

    try:
        user = User.objects.get(email=email)
    except ObjectDoesNotExist:
        return HttpResponseBadRequest("Utilisateur non trouvé")

    admin_user = get_user_from_request(request)
    if admin_user is None:
        return HttpResponseBadRequest("Utilisateur connecté non trouvé")

    if not admin_user.is_admin:
        return HttpResponseBadRequest("Vous n'êtes pas un admin")
    if user.email == admin_user.email:
        return HttpResponseBadRequest("Vous ne pouvez pas vous transferer vous même le role d'admin")
    if user.entreprise.siret != admin_user.entreprise.siret:
        return HttpResponseBadRequest("Cet utilisateur n'appartient pas a la même entreprise que vous")


    user.is_admin = True
    user.save()

    admin_user.is_admin = False
    admin_user.save()

    return HttpResponse("transfert d'admin effectué")


# endregion

# endregion

# region Middlewares
def entreprise_updated_middleware(get_response):
    target_paths = ["paperless/facture", "paperless/entreprise"]

    def middleware(request):

        path = request.path
        method = request.method

        # Si on ne trouve pas l'entreprise, cela doit être
        try:
            entreprise = get_entreprise_from_request(request)
        except:
            return get_response(request)

        target_path = ""

        for target_p in target_paths:
            if target_p in path:
                target_path = target_p
                break

        should_test = False

        if target_path != "":
            if "paperless/facture" == target_path:
                if method == "POST" or method == "PUT":
                    should_test = True
            if "paperless/entreprise" == target_path:
                if method == "PUT":
                    should_test = True

        if should_test and entreprise.is_updated:
            return HttpResponseBadRequest(
                "Les informations de l'entreprise ont été mis à jour, vous devez attendre leur vérification")

        response = get_response(request)

        return response

    return middleware


def token_middleware(get_response):
    """ Middleware permettant de vérifier la présence du token dans les cookies de la requête
    """
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


# endregion

# region Chorus

def send_to_chorus(file):
    """ envoyer une facture à chorus

    Il s'agit d'un exemple car nous n'avons pas accès la base école
    """

    # Ici on devrait écrire le code pour faire appel à l'api de chorus
    r = requests.post("chorus/api/...", files=file)

    # Et ici gérer les différentes erreurs que nous renvoi chorus
    if not r.ok:
        return "Quelque chose s'est mal passé lors de l'envoi de la facture à chorus"

    return True


def receive_from_chorus(request):
    """ Obtenir une facture de chorus

    Il s'agit d'un exemple car nous n'avons pas accès la base école
    """

    # Obtention des paramètres
    params = get_parameters(request)
    check_required_parameters(params, "siret")

    file = request.FILES['file']
    state = params["state"]
    siret = params["siret"]

    # Obtention de l'entreprise, puis de l'utilisateur
    # et vérification de leur existance
    try:
        entreprise = Entreprise.objects.get(siret=siret)
    except ObjectDoesNotExist:
        return HttpResponseBadRequest("L'entreprise n'existe pas")

    try:
        user = User.objects.get(entreprise=entreprise, is_admin=True)
    except ObjectDoesNotExist:
        return HttpResponseBadRequest("Aucun utilisateur admin de cette entreprise")
    except MultipleObjectsReturned:
        return HttpResponseBadRequest(
            "Incohérence des données, plusieurs administrateurs trouvés pour cette entreprise")

    if state is None:
        state = "NEW"

    # Insertion de la facture en base de données
    location = str(uuid.uuid4())
    default_storage.save("storage/factures/" + location, file)
    Facture.objects.create(user, location="storage/factures/" + location, state=state, taille=file.size,
                           nom=file.name.split('.')[0])

    return HttpResponse("Facture intégrée avec succès")


# endregion

# region Utilities

def get_GET_parameters(request, parameters, default_value=None) -> dict:
    ret = {}
    for parameter in parameters:
        ret[parameter] = request.GET.get(parameter, default_value)
    return ret


def get_parameters(request) -> dict:
    try:
        return json.loads(request.body.decode('utf-8'))
    except:
        return {}


def check_required_parameters(parameters: dict, required):
    """ Verifie les paramètres requis
    """
    error = None
    for key in required:
        if parameters.get(key) is None:
            error = HttpResponseBadRequest("parameter '" + key + "' is required")
            break
    return error


def get_user_from_request(request):
    admin_email = decode_token(request.COOKIES.get('token'))
    if admin_email is None:
        return None

    try:
        admin_users = User.objects.get(email=admin_email)
    except ObjectDoesNotExist:
        return None

    return admin_users


def get_entreprise_from_request(request):
    admin_email = decode_token(request.COOKIES.get('token'))
    if admin_email is None:
        return None

    try:
        admin_users = User.objects.get(email=admin_email)
    except ObjectDoesNotExist:
        return None

    return admin_users.entreprise


def delete_facture_file(facture):
    if facture.location is None:
        return

    if default_storage.exists(facture.location):
        default_storage.delete(facture.location)

    facture.location = None
    facture.save()


def decode_token(token):
    try:
        return jwt.decode(token, os.getenv("TOKEN_KEY"), algorithms=["HS256"])["token"]
    except:
        return None

# endregion
