from django.contrib import admin
from .models import User, Admin, Receptionist, Doctor, Patient, Appointment, Medical_Record, Invoice

# Register your models here.
admin.site.register(User)
admin.site.register(Admin)
admin.site.register(Receptionist)
admin.site.register(Doctor)
admin.site.register(Patient)
admin.site.register(Appointment)
admin.site.register(Medical_Record)
admin.site.register(Invoice)