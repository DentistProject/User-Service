from django.urls import path

from . import views

app_name = "users"
urlpatterns = [
    # auth/
    path("mqtt", views.test_mqtt, name="mqtt"),
    path("patient/login/", views.patient_login, name="patient-login"),
    path("dentist/login/", views.dentist_login, name="dentist-login"),
    path("patient/delete_all/", views.patient_delete_all, name="delete-all-patients"),
    path("dentist/delete_all/", views.dentist_delete_all, name="delete-all-dentists"),
    # path("signup", views.signup, name="signup"),
    # path("", views.test_token, name="test_token"),
]
