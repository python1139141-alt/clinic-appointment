from django.contrib import admin

from .models import Appointment, Doctor, Patient, Specialization


@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    search_fields = ["name"]


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ["name", "specialization", "experience", "fees"]
    search_fields = ["name", "specialization__name"]
    list_filter = ["specialization"]


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "phone"]
    search_fields = ["name", "email", "phone"]


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ["patient", "doctor", "date", "time", "status"]
    list_filter = ["status", "doctor"]
    search_fields = ["patient__name", "doctor__name", "patient__email"]
