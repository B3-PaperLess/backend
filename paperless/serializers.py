from rest_framework import serializers
from .models import User, Entreprise, Facture


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('__all__')

class EntrepriseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entreprise
        fields = ('__all__')

class FactureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Facture
        fields = ('__all__')

class FactureWithUserSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    date = serializers.DateTimeField(format='%Y-%m-%d %H:%M')
    class Meta:
        model = Facture
        fields = ('taille', 'state', 'date', 'user', 'nom')