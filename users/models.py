import json
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
# https://stackoverflow.com/questions/33259477/how-to-recreate-a-deleted-table-with-django-migrations

class Dentist(models.Model):
    first_name = models.CharField(max_length=100, blank=False)
    last_name = models.CharField(max_length=100, blank=False)
    email = models.EmailField(max_length=100, blank=False, unique=True)
    password = models.CharField(max_length=100, blank=False)
    location = models.CharField(max_length=100, blank=False)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def __str__(self) -> str:
        # return all fields
        return str(self.__dict__)

class Patient(models.Model):
    name = models.CharField(max_length=100, blank=False)
    email = models.EmailField(max_length=100, blank=False, unique=True)
    password = models.CharField(max_length=100, blank=False)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def __str__(self) -> str:
        # return all fields
        return str(self.__dict__)

# class Admin(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

class PatientToken(models.Model):
    user = models.ForeignKey(Patient, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self) -> str:
        # return all fields
        return str(self.__dict__)

class DentistToken(models.Model):
    user = models.ForeignKey(Dentist, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self) -> str:
        # return all fields
        return str(self.__dict__)
