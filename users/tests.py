import json
from django.test import TestCase

# Create your tests here.
from rest_framework.test import APITestCase
from django.urls import reverse
from .models import Patient
from users import views
from rest_framework.test import APIRequestFactory


class PatientTestCase(APITestCase):
    factory = APIRequestFactory()
    test_patient = None
    def setUp(self):
        self.test_patient = Patient.objects.create(
            name="Test Patient", email="test@example.com", password="test123"
        )

    # testing adding a patient
    def test_post_patient(self):
        view = views.PatientViewSet.as_view({'post': 'create'})
        path = '/api/v1/patients/'
        data = {
                "name": "Test Patient 2",
                "email": "test2@example.com",
                "password": "test123"
            }
        request = self.factory.post(path, data, format='json')
        response = view(request)
        self.assertEqual(response.status_code, 201) # successfully created
        self.assertEqual(Patient.objects.count(), 2) # should have 2 patients in total
        # print all patients

        response_data = json.loads(response.content)
        print(response_data)
        self.assertEqual(response_data['data']['email'], 'test2@example.com') # check if the email is correct

    # testing getting all patients
    def test_get_all_patient(self):
        view = views.PatientViewSet.as_view({'get': 'list'})
        request = self.factory.get('/api/v1/patients/')
        response = view(request)
        self.assertEqual(response.status_code, 200)

    # testing getting a patient by id
    def test_get_patient(self):
        new_patient = Patient.objects.create(
            name="new Patient",
            email="new@example.com",
            password="test123"
        )

        view = views.PatientViewSet.as_view({'get': 'retrieve'})
        request = self.factory.get('/api/v1/patients/{new_patient.id}/}')
        response = view(request, pk=new_patient.id)
        response_data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['name'], "new Patient")

    # testing updating a patient
    def test_patch_patient(self):
        path = '/api/v1/patients/'
        content = {
            "name": "Test Patient New name"
            }
        view = views.PatientViewSet.as_view({'patch': 'partial_update'})
        request = self.factory.patch(path, content, format='json')
        response = view(request, pk=self.test_patient.id)
        response_data = json.loads(response.content)
        print(response_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['data']['name'], "Test Patient New name")

    def test_delete_patient(self):
        path = '/api/v1/patients/'
        request = self.factory.delete(path)
        view = views.PatientViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=self.test_patient.id)
        self.assertEqual(response.status_code, 204) # successfully deleted should have status code 204
        self.assertFalse(Patient.objects.filter(id=self.test_patient.id).exists()) # should not exist anymore
