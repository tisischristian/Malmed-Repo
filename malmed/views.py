from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Appointment, Doctor, Patient, Receptionist
from .forms import PatientForm, AppointmentForm

def is_receptionist(user):
    return user.is_authenticated and user.is_receptionist

def custom_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, "Login successful!")
            if user.is_admin:
                return redirect("admin_dashboard")
            elif user.is_doctor:
                return redirect("doctor_dashboard")
            elif user.is_receptionist:
                return redirect("receptionist_dashboard")
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, "malmed/login.html")

@login_required
@user_passes_test(is_receptionist)
def receptionist_dashboard(request):
    appointments = Appointment.objects.all()
    return render(request, "malmed/receptionist_dashboard.html", {"appointments": appointments})

@login_required
@user_passes_test(is_receptionist)
def register_patient(request):
    if request.method == "POST":
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Patient registered successfully!")
            return redirect("receptionist_dashboard")
    else:
        form = PatientForm()
    return render(request, "malmed/register_patient.html", {"form": form})

@login_required
@user_passes_test(is_receptionist)
def schedule_appointment(request):
    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            # link the appointment to the logged-in receptionist
            appointment.receptionist = Receptionist.objects.get(user=request.user)
            appointment.save()
            messages.success(request, "Appointment scheduled successfully!")
            return redirect("receptionist_dashboard")
    else:
        form = AppointmentForm()
    return render(request, "malmed/schedule_appointment.html", {"form": form})

@login_required
def custom_logout(request):
    logout(request)
    return redirect("login")
