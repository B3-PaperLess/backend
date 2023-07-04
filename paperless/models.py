from django.db import models



class User(models.Model):
    siret = models.BigIntegerField(primary_key=True)
    nom = models.CharField(max_length=128)
    password = models.CharField(max_length=258)

    class Meta():
        db_table='user'
        app_label='paperless'


# Create your models here.
class Facture(models.Model):
    location = models.CharField(max_length=32)
    state = models.CharField(max_length=32)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    class Meta:
        db_table="facture"
        app_label='paperless'
