from django.db import models



# Create your models here.
class Facture(models.Model):
    location = models.CharField(max_length=32)

class User(models.Model):
    siret = models.BigIntegerField(primary_key=True)
    nom = models.CharField(max_length=128)
    password = models.CharField(max_length=258)
    factures = models.ManyToManyField(Facture)
