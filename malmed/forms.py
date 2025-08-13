from django import forms
from .models import Appointment, Doctor, Patient

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            'name',
            'gender',
            'date_of_birth',
            'email_address',
            'contact_number',
            'address',
            'emergency_contact'
        ]

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = [
            'patient',
            'doctor',
            'appointment_date',
            'status',
            'notes'
        ]