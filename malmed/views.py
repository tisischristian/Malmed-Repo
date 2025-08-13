from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from malmed.models import Appointment, Doctor, Patient, Receptionist, Medical_Record, Invoice
from .forms import PatientForm, AppointmentForm
from django.utils import timezone
from django.contrib import messages
from django.db.models import Q, Count
from django.contrib.auth import authenticate, login, logout

def is_admin(user):
    return user.is_authenticated and user.is_admin

def is_doctor(user):
    return user.is_authenticated and user.is_doctor

def is_receptionist(user):
    return user.is_authenticated and user.is_receptionist

def is_staff(user):
    return user.is_authenticated and (user.is_admin or user.is_doctor or user.is_receptionist)

# Create your views here.
def index(request):
    context = {
        'user': request.user,
    }
    if request.user.is_authenticated:
        if request.user.is_admin:
            return redirect('admin_dashboard')
        elif request.user.is_doctor:
            return redirect('doctor_dashboard')
        elif request.user.is_receptionist:
            return redirect('receptionist_dashboard')

    #return HttpResponse("Welcome to the Malmed CMS!")
    return render(request, 'malmed/index.html', context)

@login_required
@user_passes_test(is_doctor)
def doctor_dashboard(request):
    if request.user.is_doctor:
        today = timezone.now().date()
        doctor = get_object_or_404(Doctor, user=request.user)
        # Fetch today's appointments for the doctor

        todays_appointments = Appointment.objects.filter(
            doctor=doctor,
            appointment_date__date=today
        ).order_by('appointment_date')
        # Render the dashboard with today's appointments

        upcoming_appointments = Appointment.objects.filter(
            doctor=doctor,
            appointment_date__gt=today,
            appointment_date_date_lte=today + timezone.timedelta(days=7),
            status_in=['Scheduled', 'Confirmed']
        ).order_by('appointment_date')

        return render(request, 'malmed/doctor_dashboard.html', {
            'todays_appointments': todays_appointments,
            'upcoming_appointments': upcoming_appointments,
            'doctor': doctor
        })


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    today = timezone.now().date()

    doctor_count = Doctor.objects.filter(is_active=True).count()
    patient_count = Patient.objects.count()
    appointment_count = Appointment.objects.filter()


    if request.user.is_admin:
        # Assuming you have models for Doctor, Patient, and Appointment
        doctor_count = Doctor.objects.count()
        patient_count = Patient.objects.count()
        appointment_count = Appointment.objects.count()
        
        return render(request, 'malmed/admin_dashboard.html', {
            'doctor_count': doctor_count,
            'patient_count': patient_count,
            'appointment_count': appointment_count
        })
    else:
        return render(request, 'malmed/unauthorized.html')
    
@login_required
def receptionist_dashboard(request):
    if request.user.is_receptionist:
        # Assuming you have a model for Appointment
        appointments = Appointment.objects.all()
        return render(request, 'malmed/receptionist_dashboard.html', {
            'appointments': appointments
        })
    else:
        return render(request, 'malmed/unauthorized.html')
    

@login_required
def register_patient(request):
    if request.user.is_receptionist:
        # Handle patient registration form submission
        if request.method == 'POST':
            form = PatientForm(request.POST)
            if form.is_valid():
                form.save()
                return HttpResponse("Patient registered successfully!")
        else:
            form = PatientForm()
        
        return render(request, 'malmed/register_patient.html', {'form': form})
    else:
            return render(request, 'malmed/unauthorized.html')

@login_required
def schedule_appointment(request):
    if request.user.is_receptionist:
        if request.method == 'POST':
            form = AppointmentForm(request.POST)
            if form.is_valid():
                form.save()
                return HttpResponse("Appointment scheduled successfully!")
        else:
            form = AppointmentForm()
        
        return render(request, 'malmed/schedule_appointment.html', {'form': form})
    else:
        return render(request, 'malmed/unauthorized.html')
    

def custom_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Redirect based on role
            if user.is_admin or user.is_superuser:
                return redirect("admin_dashboard")
            elif user.is_doctor:
                return redirect("doctor_dashboard")
            elif user.is_receptionist:
                return redirect("receptionist_dashboard")
            else:
                return redirect("index")
        else:
            return render(request, "malmed/login.html", {"error": "Invalid credentials"})

    return render(request, "malmed/login.html")