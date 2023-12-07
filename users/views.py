import datetime
import json
from django.shortcuts import get_object_or_404, render
from django.http import Http404, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from .serializers import (
    PatientSerializer,
    DentistSerializer,
    PatientTokenSerializer,
    DentistTokenSerializer,
)

from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

# Create your views here.

from mqtt_handler import MQTTHandler
from .models import Patient, Dentist, PatientToken, DentistToken

broker_address = "06c9231f22d4457abe0282a4302eda82.s2.eu.hivemq.cloud"
port = 8883
topic = "Userservice"
username = "toothcheck"
password = "5vuiygrR6vygB!"

logger_topic = "Logger"

mqtt_handler = MQTTHandler(broker_address, port, topic, username, password)
mqtt_handler.connect()


class PatientViewSet(ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    allowed_methods = ["get", "post", "patch", "delete"]

    # GET all patients
    def list(self, request):
        mqtt_logger(request, "GET")
        patients = Patient.objects.all().values()
        patients_list = list(patients)
        if len(patients_list) == 0:
            return JsonResponse({"message": "No patients found!"}, status=404)
        return JsonResponse({"patients": patients_list}, safe=False, status=200)

    # GET patient by id
    # Needs authentication
    def retrieve(self, request, pk=None):
        mqtt_logger(request, "GET")
        try:
            patient_authenticate(request.headers["Authorization"])
            patient = Patient.objects.get(pk=pk)
            serializer = PatientSerializer(patient)
            return JsonResponse(serializer.data, safe=False, status=200)
        except Patient.DoesNotExist:
            return JsonResponse({"message": "Patient not found!"}, status=404)
        except NotFound as e:
            return JsonResponse({"message": str(e)}, status=404)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)

    # POST new patient
    def create(self, request):
        mqtt_logger(request, "POST")
        try:
            data = json.loads(request.body)
            required_fields = ["first_name", "last_name", "email", "password"]

            for each in required_fields:
                if not data[each]:
                    raise ValidationError(f"{each.capitalize()} is required")

            validate_email(data["email"])  # From django.core.validators
            hashed_password = make_password(data["password"])

            new_patient = Patient(
                first_name=data["first_name"],
                last_name=data["last_name"],
                email=data["email"],
                password=hashed_password,
                phone_number=data["phone_number"],
            )
            serializer = PatientSerializer(new_patient)
            new_patient.save()
            return JsonResponse(
                {
                    "message": "Patient was added successfully!",
                    "data": serializer.data,
                },
                status=201,
            )
        except ValidationError as e:
            return JsonResponse({"message": f"{str(e)} is required"}, status=400)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)

    # PATCH patient by id
    # Need authentication
    def partial_update(self, request, pk=None):
        mqtt_logger(request, "PATCH")
        try:
            patient_authenticate(request.headers["Authorization"])
            patient = Patient.objects.get(pk=pk)
            request_data = json.loads(request.body)
            for each in request_data.keys():
                if hasattr(patient, each):
                    setattr(patient, each, request_data[each])
                patient.save()
            serializer = PatientSerializer(patient)
            return JsonResponse(
                {
                    "message": "Patient was updated successfully!",
                    "data": serializer.data,
                },
                status=200,
            )

        except Patient.DoesNotExist:
            return JsonResponse({"message": "Patient not found!"}, status=404)

    # DELETE patient by id
    # Need authentication
    def destroy(self, request, pk=None):
        mqtt_logger(request, "DELETE")
        try:
            patient_authenticate(request.headers["Authorization"])
            patient = Patient.objects.get(pk=pk)
            patient.delete()
            return JsonResponse(
                {"message": "Patient was deleted successfully!"}, status=204
            )
        except Patient.DoesNotExist:
            return JsonResponse({"message": "Patient not found!"}, status=404)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)


@api_view(["POST"])
def patient_login(request):
    try:
        if not request.data["password"] or not request.data["email"]:
            return Response(
                {"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )

        user = get_object_or_404(Patient, email=request.data["email"])
        if not check_password(
            request.data["password"], user.password
        ):  # Check if passwork is valid
            return Response(
                {"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )

        token, created = PatientToken.objects.get_or_create(user=user)
        tokenserializer = PatientTokenSerializer(token)
        userserializer = PatientSerializer(user)
        # The token returned should be stored on the client side and used for future requests
        return JsonResponse(
            {
             "user": userserializer.data,
             "token": tokenserializer.data["token"]
            },
            status=200
            )
    except KeyError as e:
        return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Http404 as e:
        return Response({"message": str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return JsonResponse({"message": str(e)}, status=500)

def patient_authenticate(token):
    patient_timeout()
    if not token:
        raise NotFound("Unauthorized")
    print(token)
    get_object_or_404(PatientToken, token=token)


def patient_timeout():
    current_time = datetime.datetime.now()
    expired_tokens = PatientToken.objects.filter(
        created_at__lt=datetime.timezone.now() - datetime.timedelta(hours=48)
    )  # Filter tokens older than 48 hours, __lt = less than
    expired_tokens.delete()


class DentistViewSet(ModelViewSet):
    queryset = Dentist.objects.all()
    serializer_class = PatientSerializer
    allowed_methods = ["get", "post", "patch", "delete"]

    # GET all dentists
    def list(self, request):
        mqtt_logger(request, "GET")
        dentists = Dentist.objects.all().values()
        dentists_list = list(dentists)
        if len(dentists_list) == 0:
            return JsonResponse({"message": "No dentists found!"}, status=404)
        return JsonResponse({"dentists": dentists_list}, safe=False, status=200)

    # GET dentist by id
    # Needs authentication
    def retrieve(self, request, pk=None):
        mqtt_logger(request, "GET")
        try:
            dentist_authenticate(request.headers["Authorization"])
            dentist = Dentist.objects.get(pk=pk)
            serializer = DentistSerializer(dentist)
            return JsonResponse(serializer.data, safe=False, status=200)
        except Dentist.DoesNotExist:
            return JsonResponse({"message": "Dentist not found!"}, status=404)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)

    # POST new dentist
    def create(self, request):
        mqtt_logger(request, "POST")
        try:
            data = json.loads(request.body)
            required_fields = [
                "name",
                "email",
                "password",
                "location",
            ]

            for each in required_fields:
                if not data[each]:
                    raise ValidationError(f"{each.capitalize()} is required")

            validate_email(data["email"])  # From django.core.validators
            hashed_password = make_password(data["password"])

            new_dentist = Dentist(
                name=data["name"],
                email=data["email"],
                password=hashed_password,
                location=data["location"],
            )
            serializer = DentistSerializer(new_dentist)
            new_dentist.save()
            return JsonResponse(
                {"message": "Dentist was added successfully!", "data": serializer.data},
                status=201,
            )
        except ValidationError as e:
            return JsonResponse({"message": f"{str(e)} is required"}, status=400)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)

    # PATCH dentist by id
    # Need authentication
    def partial_update(self, request, pk=None):
        mqtt_logger(request, "PATCH")
        try:
            dentist_authenticate(request.headers["Authorization"])
            dentist = Dentist.objects.get(pk=pk)
            request_data = json.loads(request.body)
            for each in request_data.keys():
                if hasattr(dentist, each):
                    setattr(dentist, each, request_data[each])
                dentist.save()
            serializer = DentistSerializer(dentist)
            return JsonResponse(
                {
                    "message": "Dentist was updated successfully!",
                    "data": serializer.data,
                },
                status=200,
            )

        except Dentist.DoesNotExist:
            return JsonResponse({"message": "Dentist not found!"}, status=404)

    # DELETE dentist by id
    # Need authentication
    def destroy(self, request, pk=None):
        mqtt_logger(request, "DELETE")
        try:
            dentist_authenticate(request.headers["Authorization"])
            dentist = Dentist.objects.get(pk=pk)
            dentist.delete()
            return JsonResponse(
                {"message": "Dentist was deleted successfully!"}, status=204
            )
        except Dentist.DoesNotExist:
            return JsonResponse({"message": "Dentist not found!"}, status=404)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)


@api_view(["POST"])
def dentist_login(request):
    try:
        if not request.data["password"] or not request.data["email"]:
            return Response(
                {"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )

        user = get_object_or_404(Dentist, email=request.data["email"])
        if not check_password(
            request.data["password"], user.password
        ):  # Check if passwork is valid
            return Response(
                {"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )

        token, created = DentistToken.objects.get_or_create(user=user)
        token_serializer = DentistTokenSerializer(token)
        dentist_serializer = DentistSerializer(user)
        print(request.user)
        # The token returned should be stored on the client side and used for future requests
        return JsonResponse(
            {
                "dentist": dentist_serializer.data,
                "token": token_serializer.data["token"]
            }, status=200
        )
    except KeyError as e:
        return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Http404 as e:
        return Response({"message": str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return JsonResponse({"message": str(e)}, status=500)


def dentist_authenticate(token):
    dentist_timeout()
    if not token:
        raise NotFound("Unauthorized")
    print(token)
    get_object_or_404(DentistToken, token=token)


def dentist_timeout():
    current_time = datetime.datetime.now()
    expired_tokens = DentistToken().objects.filter(
        created_at__lt=datetime.timezone.now() - datetime.timedelta(days=7)
    )  # Filter tokens older than 7 days, __lt = less than
    expired_tokens.delete()


def mqtt_logger(request, method):
    # format string into : method url current time
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


# @api_view(['POST'])
# def login(request):
#     try:
#         if not request.data['password'] or not request.data['email']:
#             return Response({"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

#         user = get_object_or_404(Patient, email=request.data['email'])
#         if not check_password(request.data['password'], user.password):
#             return Response({"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
#         token, created = Token.objects.get(user=user.user)
#         serializer = PatientSerializer(user)
#         return Response({
#             "token": token.key,
#             "patient": serializer.data
#         }, status=status.HTTP_200_OK)
#     except KeyError as e:
#         return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['POST'])
# def signup(request):
#     serializer = PatientSerializer(data=request.data)
#     if serializer.is_valid():
#         serializer.save()
#         user = Patient.objects.get(email=serializer.data['email'])
#         token = Token.objects.create(user=user)
#         return Response({
#             "token": token.key,
#             "patient": serializer.data
#         }, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# @api_view(['GET'])
# def test_token(request):
#     return Response({})
