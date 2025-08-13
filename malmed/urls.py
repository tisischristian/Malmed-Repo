from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('receptionist/dashboard/', views.receptionist_dashboard, name='receptionist_dashboard'),
    #path('login/', auth_views.LoginView.as_view(template_name='malmed/login.html'), name='login'),
    path('receptionist/register_patient/', views.register_patient, name='register_patient'),
    path('receptionist/schedule_appointment/', views.schedule_appointment, name='schedule_appointment'),
    path("login/", views.custom_login, name="login"),

]
