from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.http import HttpResponse

# Create your models here.

# --- Custom User Model with Role-based Access ---
class User(AbstractUser):
    is_admin = models.BooleanField(default=False)
    is_doctor = models.BooleanField(default=False)
    is_receptionist = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.is_staff = True
            self.is_admin = True
            self.is_doctor = False
            self.is_receptionist = False

        elif self.is_admin or self.is_doctor or self.is_receptionist:
            self.is_staff = True
        else:
            self.is_staff = False
            
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
    
# --- Abstract Base Class for Shared Fields ---
class Person(models.Model):
    name = models.CharField(max_length=100)
    email_address = models.EmailField(unique=True)
    contact_number = models.CharField(max_length=15, unique=True)
    address = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Admin(Person):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} (Admin)"
    
    class Meta:
        verbose_name = "Administrator"
        verbose_name_plural = "Administrators"
    
class Receptionist(Person):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    registration_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}, Receptionist"
    
    class Meta:
        ordering = ['name']


class Doctor(Person):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Dr. {self.name} - {self.specialization}"
    class Meta:
        ordering = ['name']


class Gender(models.TextChoices):
    male = "M", "Male"
    female = "F", "Female"
    other = "O", "Other"
    
class Patient(Person):
    # GENDER_CHOICES = [
    #     ('M', 'Male'),
    #     ('F', 'Female'),
    # ]

    gender = models.CharField(max_length=10, choices=Gender.choices, default=Gender.female)

    #gender = models.CharField(max_length=10)
    date_of_birth = models.DateField()
    emergency_contact = models.CharField(max_length=100)

    @property
    def age(self):
        today = timezone.now().date()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    def clean(self):
        if self.date_of_birth > timezone.now().date():
            raise ValidationError("Date of birth cannot be in the future.")
        if self.age > 150:
            raise ValidationError("Patient age cannot exceed 150 years.")

    def __str__(self):
        return f"{self.name}, (Age: {self.age})"
    
    class Meta:
        ordering = ['name']


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('Scheduled', 'Scheduled'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.RESTRICT)
    receptionist = models.ForeignKey(Receptionist, on_delete=models.CASCADE)
    appointment_date = models.DateTimeField()
    duration = models.DurationField(default=timezone.timedelta(minutes=30))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Scheduled')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_upcoming(self):
        return self.appointment_date > timezone.now() and self.status in ['Scheduled', 'Confirmed']
    
    @property
    def is_today(self):
        return self.appointment_date.date() == timezone.now().date()
    
    def clean(self):
        if self.appointment_date <= timezone.now():
            raise ValidationError("Appointment date cannot be in the past.")
        if self.duration <= timezone.timedelta(minutes=0):
            raise ValidationError("Appointment duration must be greater than zero.")
        if not self.doctor.is_active:
            raise ValidationError("Cannot schedule appointment with an inactive doctor.")
    def __str__(self):
        return f"Appointment for {self.patient.name} with Dr. {self.doctor.name} on {self.appointment_date.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ['appointment_date']
        unique_together = ('doctor', 'appointment_date')

class Medical_Record(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True)
    visit_date = models.DateTimeField(default=timezone.now)
    symptoms = models.TextField(blank=True, null=True)
    diagnosis = models.TextField()
    treatment = models.TextField()
    prescription = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Medical Record for {self.patient.name} by Dr. {self.doctor.name} - {self.visit_date}"
    
    class Meta:
        ordering = ['-visit_date']
        unique_together = ('patient', 'visit_date')
    
class Invoice(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('Paid', 'Paid'),
        ('Unpaid', 'Unpaid'),
        ('Pending', 'Pending'),
        ('Overdue', 'Overdue'),
    ]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    invoice_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Pending')

    @property
    def is_overdue(self):
        return (self.due_date < timezone.now().date() and self.status == 'Pending')
    
    def save(self, *args, **kwargs):
        if self.due_date and self.due_date < self.invoice_date:
            raise ValidationError("Due date cannot be before the invoice date.")
        super().save(*args, **kwargs)
    

    def __str__(self):
        return f"Invoice for {self.patient.name} - MWK{self.amount} on {self.invoice_date}"
    
    class Meta:
        ordering = ['-invoice_date']
        unique_together = ('patient', 'invoice_date')