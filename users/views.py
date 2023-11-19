import datetime
import json
from django.shortcuts import render
from django.http import Http404, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password, check_password
from .serializers import PatientSerializer

from rest_framework.decorators import api_view
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.exceptions import NotFound

# Create your views here.

from mqtt_handler import MQTTHandler
from .models import Patient

broker_address = "06c9231f22d4457abe0282a4302eda82.s2.eu.hivemq.cloud"
port = 8883
topic = "Userservice"
username = "toothcheck"
password = "5vuiygrR6vygB!"

logger_topic = "Logger"

mqtt_handler = MQTTHandler(broker_address, port, topic, username, password)
mqtt_handler.connect()

class PatientViewSet(ModelViewSet):
    app_name = "patient"
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    allowed_methods = ['get', 'post', 'patch', 'delete']

    # GET all patients
    def list(self, request):
        mqtt_logger(request, "GET")
        patients = Patient.objects.all().values()
        patients_list = list(patients)
        if len(patients_list) == 0:
            return JsonResponse({"message": "No patients found!"}, status=404)
        return JsonResponse({"patients": patients_list}, safe=False, status=200)

    # GET patient by id
    def retrieve(self, request, pk=None):
        mqtt_logger(request, "GET")
        try:
            patient = Patient.objects.get(pk=pk)
            serializer = PatientSerializer(patient)
            return JsonResponse(serializer.data, safe=False, status=200)
        except Patient.DoesNotExist:
            return JsonResponse({"message": "Patient not found!"}, status=404)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)


    # POST new patient
    def create(self, request):
        mqtt_logger(request, "POST")
        try:
            data = json.loads(request.body)
            if not data["name"]:
                raise ValidationError("Name is required")
            if not data["email"]:
                raise ValidationError("Email is required")
            if not data["password"]:
                raise ValidationError("Password is required")

            validate_email(data["email"])  # From django.core.validators
            hashed_password = make_password(data["password"])

            new_patient = Patient(
                name=data["name"],
                email=data["email"],
                password=hashed_password,
            )
            serializer = PatientSerializer(new_patient)
            new_patient.save()
            return JsonResponse(
                {
                    "message": "Patient was added successfully!",
                    "data": serializer.data
                },
                status=201,
            )
        except ValidationError as e:
            return JsonResponse({"message": e.message}, status=400)
        except KeyError as e:
            return JsonResponse({"message": f"{str(e)} is required"}, status=400)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)


    # PATCH patient by id
    def partial_update(self, request, pk=None):
        mqtt_logger(request, "PATCH")
        try:
            patient = Patient.objects.get(pk=pk)
            request_data = json.loads(request.body)
            for each in request_data.keys():
                if hasattr(patient, each):
                    setattr(patient, each, request_data[each])
                patient.save()
            serializer = PatientSerializer(patient)
            return JsonResponse({"message": "Patient was updated successfully!", "data": serializer.data}, status=200)

        except Patient.DoesNotExist:
            return JsonResponse({"message": "Patient not found!"}, status=404)


    # DELETE patient by id
    def destroy(self, request, pk=None):
        mqtt_logger(request, "DELETE")
        try:
            patient = Patient.objects.get(pk=pk)
            patient.delete()
            return JsonResponse({"message": "Patient was deleted successfully!"}, status=200)
        except Patient.DoesNotExist:
            return JsonResponse({"message": "Patient not found!"}, status=404)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)



def mqtt_logger(request, method):
    #format string into : method url current time
    formatted_string = f"{method} {request.path} {datetime.datetime.now()}"
    mqtt_handler.client.publish(logger_topic, formatted_string)


def index(request):
    return HttpResponse("Patient app is running")


def publish_message(message):
    # Publish a message to the specified topic
    try:
        message_info = mqtt_handler.client.publish(topic, message)
        message_info.wait_for_publish(1.5)
    except TimeoutError as err:
        return JsonResponse(err)
    return HttpResponse(message_info.is_published())

def test_mqtt(request):
    publish_message("Hello from Django!")
    return HttpResponse("Message published")
