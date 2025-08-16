from django.urls import path
from . import views

urlpatterns = [
    path("", views.custom_login, name="login"),
    path("logout/", views.custom_logout, name="logout"),
    path("receptionist/dashboard/", views.receptionist_dashboard, name="receptionist_dashboard"),
    path("receptionist/register_patient/", views.register_patient, name="register_patient"),
    path("receptionist/schedule_appointment/", views.schedule_appointment, name="schedule_appointment"),
]
