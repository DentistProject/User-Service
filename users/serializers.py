from rest_framework import serializers
from .models import Patient, Dentist


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ["id", "name", "email", "password"]

class DentistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dentist
        fields = ["id", "first_name", "last_name", "email", "password", "location"]
