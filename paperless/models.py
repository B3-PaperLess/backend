from django.db import models



class User(models.Model):
    siret = models.BigIntegerField(primary_key=True)
    nom = models.CharField(max_length=128, blank=False, null=False)
    password = models.CharField(max_length=258, blank=False, null=False)

    class Meta():
        db_table='user'
        app_label='paperless'


# Create your models here.
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
