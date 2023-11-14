import uuid
from django.db import models

# Create your models here.
# https://stackoverflow.com/questions/33259477/how-to-recreate-a-deleted-table-with-django-migrations


class Patient(models.Model):
    name = models.CharField(max_length=100, blank=False, default="name")
    email = models.EmailField(max_length=100, blank=False, unique=True, default="email")
    password = models.CharField(max_length=100, blank=False, default="password")
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def __str__(self) -> str:
        return self.name


# class Dentist(models.Model):
#     name = models.CharField(max_length=100, blank=False)
#     location = models.CharField(max_length=100, blank=False)
#     patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

# class Admin(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
