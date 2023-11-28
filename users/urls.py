from django.urls import path

from . import views

app_name = "users"
urlpatterns = [
    # auth/
    path("mqtt", views.test_mqtt, name="mqtt"),
    path("patient/login/", views.patient_login, name="patient-login"),
    path("dentist/login/", views.dentist_login, name="dentist-login"),
    # path("signup", views.signup, name="signup"),
    # path("", views.test_token, name="test_token"),
]
