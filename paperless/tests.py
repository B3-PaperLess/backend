from django.test import TestCase
from . import models

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
            location="location",
            state="state",
            user=user,
        )

    def test_get(self):
        facture = models.Facture.objects.get(location="location")
        self.assertEqual(facture.state, "state")
        self.assertEqual(facture.user.email, "test@test.test")
        self.assertEqual(facture.user.nom, "nom")
        self.assertEqual(facture.user.prenom, "prenom")
        self.assertEqual(facture.user.num_tel, "0123456789")
        self.assertEqual(facture.user.password, "password")
        self.assertEqual(facture.user.is_admin, False)
        self.assertEqual(facture.user.entreprise.siret, 12345678901234)
        self.assertEqual(facture.user.entreprise.nom, "entreprise")
        self.assertEqual(facture.user.entreprise.adresse, "adresse")
        self.assertEqual(facture.user.entreprise.ville, "ville")
    
    def test_update(self):
        facture = models.Facture.objects.get(location="location")
        facture.state = "state2"
        facture.save()
        facture = models.Facture.objects.get(location="location")
        self.assertEqual(facture.state, "state2")
        self.assertEqual(facture.user.email, "test@test.test")
        self.assertEqual(facture.user.nom, "nom")
        self.assertEqual(facture.user.prenom, "prenom")
        self.assertEqual(facture.user.num_tel, "0123456789")
        self.assertEqual(facture.user.password, "password")
        self.assertEqual(facture.user.is_admin, False)
        self.assertEqual(facture.user.entreprise.siret, 12345678901234)
        self.assertEqual(facture.user.entreprise.nom, "entreprise")
        self.assertEqual(facture.user.entreprise.adresse, "adresse")
        self.assertEqual(facture.user.entreprise.ville, "ville")
      
    def test_delete(self):
        facture = models.Facture.objects.get(location="location")
        facture.delete()
        with self.assertRaises(models.Facture.DoesNotExist):
            facture = models.Facture.objects.get(location="location")

#endregion

#endregion

#region Views tests

#endregion

