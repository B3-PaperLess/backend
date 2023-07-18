from django.test import TestCase
from . import models
from django.urls import reverse
from django.test import Client
import bcrypt
from datetime import datetime
client = Client()

#region Models tests

#region Entreprise tests
class EntrepriseTestCase(TestCase):
    def setUp(self):
        models.Entreprise.objects.create(
            siret=12345678901234,
            nom="entreprise",
            adresse="adresse",
            ville="ville",
        )

    def test_get(self):
        entreprise = models.Entreprise.objects.get(siret=12345678901234)
        self.assertEqual(entreprise.nom, "entreprise")
        self.assertEqual(entreprise.adresse, "adresse")
        self.assertEqual(entreprise.ville, "ville")

    def test_update(self):
        entreprise = models.Entreprise.objects.get(siret=12345678901234)
        entreprise.nom = "entreprise2"
        entreprise.adresse = "adresse2"
        entreprise.ville = "ville2"
        entreprise.save()
        entreprise = models.Entreprise.objects.get(siret=12345678901234)
        self.assertEqual(entreprise.nom, "entreprise2")
        self.assertEqual(entreprise.adresse, "adresse2")
        self.assertEqual(entreprise.ville, "ville2")
    
    def test_create(self):
        entreprise = models.Entreprise.objects.create(
            siret=12345678901235,
            nom="entreprise3",
            adresse="adresse3",
            ville="ville3",
        )
        entreprise = models.Entreprise.objects.get(siret=12345678901235)
        self.assertEqual(entreprise.nom, "entreprise3")
        self.assertEqual(entreprise.adresse, "adresse3")
        self.assertEqual(entreprise.ville, "ville3")
      
    def test_delete(self):
        entreprise = models.Entreprise.objects.get(siret=12345678901234)
        entreprise.delete()
        with self.assertRaises(models.Entreprise.DoesNotExist):
            entreprise = models.Entreprise.objects.get(siret=12345678901234)

#endregion

#region User tests
class UserTestCase(TestCase):
    def setUp(self):
        entreprise = models.Entreprise.objects.create(
            siret=12345678901234,
            nom="entreprise",
            adresse="adresse",
            ville="ville",
        )
        models.User.objects.create(
            email="test@test.test",
            nom="nom",
            prenom="prenom",
            num_tel="0123456789",
            password="password",
            is_admin=False,
            entreprise=entreprise,
        )
    
    def test_get(self):
        user = models.User.objects.get(email="test@test.test")
        self.assertEqual(user.nom, "nom")
        self.assertEqual(user.prenom, "prenom")
        self.assertEqual(user.num_tel, "0123456789")
        self.assertEqual(user.password, "password")
        self.assertEqual(user.is_admin, False)
        self.assertEqual(user.entreprise.siret, 12345678901234)
        self.assertEqual(user.entreprise.nom, "entreprise")
        self.assertEqual(user.entreprise.adresse, "adresse")
        self.assertEqual(user.entreprise.ville, "ville")
      
    def test_update(self):
        user = models.User.objects.get(email="test@test.test")
        user.nom = "nom2"
        user.prenom = "prenom2"
        user.num_tel = "9876543210"
        user.password = "password2"
        user.is_admin = True
        user.save()
        user = models.User.objects.get(email="test@test.test")
        self.assertEqual(user.nom, "nom2")
        self.assertEqual(user.prenom, "prenom2")
        self.assertEqual(user.num_tel, "9876543210")
        self.assertEqual(user.password, "password2")
        self.assertEqual(user.is_admin, True)
        self.assertEqual(user.entreprise.nom, "entreprise")
        self.assertEqual(user.entreprise.adresse, "adresse")
        self.assertEqual(user.entreprise.ville, "ville")

    def test_delete(self):
        user = models.User.objects.get(email="test@test.test")
        user.delete()
        with self.assertRaises(models.User.DoesNotExist):
            user = models.User.objects.get(email="test@test.test")
      
#endregion

#region Facture tests
class FactureTestCase(TestCase):
    def setUp(self):
        entreprise = models.Entreprise.objects.create(
            siret=12345678901234,
            nom="entreprise",
            adresse="adresse",
            ville="ville",
        )
        user = models.User.objects.create(
            email="test@test.test",
            nom="nom",
            prenom="prenom",
            num_tel="0123456789",
            password="password",
            is_admin=False,
            entreprise=entreprise,
        )        
        models.Facture.objects.create(
            nom = "facture",
            location = "location",
            taille = 1234567890,
            state = "state",
            date = "2020-01-01",
            user = user,
        )
    
    def test_get(self):
        facture = models.Facture.objects.get(nom="facture")
        self.assertEqual(facture.location, "location")
        self.assertEqual(facture.taille, 1234567890)
        self.assertEqual(facture.state, "state")
        

    def test_update(self):
        facture = models.Facture.objects.get(nom="facture")
        facture.location = "location2"
        facture.taille = 9876543210
        facture.state = "state2"
        facture.save()
        facture = models.Facture.objects.get(nom="facture")
        self.assertEqual(facture.location, "location2")
        self.assertEqual(facture.taille, 9876543210)
        self.assertEqual(facture.state, "state2")

    def test_delete(self):
        facture = models.Facture.objects.get(nom="facture")
        facture.delete()
        with self.assertRaises(models.Facture.DoesNotExist):
            facture = models.Facture.objects.get(nom="facture")

#endregion

#endregion

#region Views tests

class AuthentificationTestCase(TestCase):
    def setUp(self):
        entreprise = models.Entreprise.objects.create(
            siret=12345678901234,
            nom="entreprise",
            adresse="adresse",
            ville="ville",
        )
        password = "password"
        user = models.User.objects.create(
            email="test@test.com",
            nom="nom",
            prenom="prenom",
            num_tel="0123456789",
            password=bcrypt.hashpw(password.encode(),bcrypt.gensalt()).decode(),
            is_admin=False,
            entreprise=entreprise,
        )
        user.save()
    
    def test_login(self):
        url = reverse('connect')
        response = client.post(url, {'email': 'test@test.com', 'password': 'password'}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['user']['email'], 'test@test.com')

    def test_login_wrong_input(self):
        url = reverse('connect')
        response = client.post(url, {'email': 'wrongtest@test.com', 'password': 'wrongpassword'}, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'Email ou mot de passe invalide')
    
    def test_register(self):
        url = reverse('signup')
        password = "TEST_1234"
        newUser = {
                "nom":"test",
                "prenom":"test",
                "email":"testSignUp@test.com",
                "num_tel":"0000000000",
                "password": password,
                "passwordAgain": password,
                "siret":"00000000000000",
                "raison_social":"test",
                "adresse":"test",
                "ville":"test"
            }
        response = client.post(url, newUser, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        content = response.json()
        self.assertEqual(content['user']['email'], 'testSignUp@test.com')
        self.assertEqual(content['user']['nom'], 'test')
        self.assertEqual(content['user']['prenom'], 'test')
        self.assertEqual(content['user']['num_tel'], '0000000000')
        self.assertEqual(content['user']['is_admin'], True)
        self.assertEqual(content['user']['entreprise'], '00000000000000')
        self.assertTrue(bcrypt.checkpw(password.encode(), content['user']['password'].encode()))

#endregion

