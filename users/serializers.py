from rest_framework import serializers
from .models import Patient, Dentist, PatientToken, DentistToken


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ["id", "name", "email", "password"]

class DentistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dentist
        fields = ["id", "first_name", "last_name", "email", "password", "location"]

class PatientTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientToken
        fields = ["user", "token"]

class DentistTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = DentistToken
        fields = ["user", "token"]
