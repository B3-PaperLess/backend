from django.db import models

class Entreprise(models.Model):
    siret = models.BigIntegerField(primary_key=True)
    nom = models.CharField(max_length=64, blank=False, null=False)
    adresse = models.CharField(max_length=255, blank=False, null=False)
    ville = models.CharField(max_length=255, blank=False, null=False)
    valide = models.BooleanField(default=False, null=False, blank=False)
    class Meta:
        db_table='entreprise'
        app_label='paperless'

class User(models.Model):
    email = models.EmailField(unique=True, blank=False, null=False)
    nom = models.CharField(max_length=128, blank=True,)
    prenom = models.CharField(max_length=64, blank=True,)
    num_tel = models.CharField(max_length=10, blank=True,)
    password = models.CharField(max_length=258, blank=False, null=False)
    is_admin = models.BooleanField(default=False)
    entreprise = models.ForeignKey(
        Entreprise,
        on_delete=models.CASCADE
    )

    class Meta():
        db_table='user'
        app_label='paperless'


class Facture(models.Model):
    location = models.CharField(max_length=32, unique=True, blank=False, null=False)
    state = models.CharField(max_length=32, blank=False, null=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    class Meta:
        db_table="facture"
        app_label='paperless'