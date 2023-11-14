from django.test import TestCase

# Create your tests here.
from django.test import TestCase, Client
from django.urls import reverse
from .models import Patient


class PatientTestCase(TestCase):
    def setUp(self):
        Patient.objects.create(
            name="Test Patient", email="test@example.com", password="test123"
        )

    def test_post_patient(self):
        client = Client()
        url = "patient/post"
        response = client.post(
            url,
            {
                "name": "Test2 Patient",
                "email": "Test2@example.com",
                'password': 'test123'
            }
        )
        self.assertEqual(response.status_code, 201)


    def test_get_all_patient(self):
        client = Client()
        response = client.get("/patient/")
        print(response.content)
        self.assertEqual(response.status_code, 200)

    def test_get_patient_by_id(self):
        client = Client()
        response = client.get("/patient/1")
        self.assertEqual(response.status_code, 404)







