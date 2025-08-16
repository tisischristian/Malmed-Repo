from django import forms
from django.forms.widgets import SplitDateTimeWidget
from django.utils import timezone

from .models import Appointment, Doctor, Patient, Gender

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['name', 'email_address', 'contact_number', 'address', 'gender', 'date_of_birth', 'emergency_contact']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'email_address': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Primary Phone Number'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street Address'}),
            'gender': forms.Select(attrs={'class': 'form-select'}, choices=Gender.choices),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'max': timezone.now().date()}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name and Phone of Emergency Contact'}),
        }
        labels = {
            'name': 'Full Name',
            'email_address': 'Email Address',
            'contact_number': 'Phone Number',
            'address': 'Residential Address',
            'gender': 'Gender',
            'date_of_birth': 'Date of Birth',
            'emergency_contact': 'Emergency Contact',
        }
        help_texts = {
            'contact_number': 'Include country code if outside Malawi',
            'emergency_contact': 'Who should we contact in case of emergency?',
        }
class AppointmentForm(forms.ModelForm):
    appointment_date = forms.SplitDateTimeField(
        widget=SplitDateTimeWidget(
            date_attrs={"type": "date", "class": "form-control"},
            time_attrs={"type": "time", "class": "form-control"},
        )
    )

    class Meta:
        model = Appointment
        fields = ["patient", "doctor", "appointment_date", "duration", "status", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        }