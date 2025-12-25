from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import (
    AppointmentFilterForm,
    AppointmentForm,
    AppointmentStatusForm,
    DoctorForm,
    SpecializationForm,
    PatientSignupForm,
)
from .models import Appointment, Doctor, Patient, Specialization
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required


def home(request):
    stats = {
        "doctor_count": Doctor.objects.count(),
        "patient_count": Patient.objects.count(),
        "appointment_count": Appointment.objects.count(),
        "pending_count": Appointment.objects.filter(
            status=Appointment.STATUS_PENDING
        ).count(),
    }
    featured_doctors = Doctor.objects.select_related("specialization")[:6]
    return render(
        request,
        "home.html",
        {
            "stats": stats,
            "featured_doctors": featured_doctors,
        },
    )


def signup(request):
    form = PatientSignupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Account created successfully.")
        return redirect("home")
    return render(request, "registration/signup.html", {"form": form})



def doctor_list(request):
    specialization_id = request.GET.get("specialization")
    doctors = Doctor.objects.select_related("specialization")
    specializations = Specialization.objects.all()
    if specialization_id:
        doctors = doctors.filter(specialization_id=specialization_id)
    return render(
        request,
        "doctors.html",
        {"doctors": doctors, "specializations": specializations},
    )


def doctor_detail(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    return render(request, "doctor_detail.html", {"doctor": doctor})



@login_required
def book_appointment(request):
    form = AppointmentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            patient = request.user.patient
        except Patient.DoesNotExist:
            messages.error(request, "Patient profile not found.")
            return redirect("home")

        Appointment.objects.create(
            patient=patient,
            doctor=form.cleaned_data["doctor"],
            date=form.cleaned_data["date"],
            time=form.cleaned_data["time"],
            notes=form.cleaned_data["notes"],
        )
        messages.success(
            request,
            "Your appointment request has been submitted. Our team will confirm soon.",
        )
        return redirect("appointment_success")
    
    # Pre-fill name and email/phone if possible? 
    # The form currently doesn't accept initial values nicely without modifying form class or passing initial dictionary.
    # For now, just render.
    return render(
        request,
        "book_appointment.html",
        {"form": form, "doctors": Doctor.objects.all()},
    )


def appointment_success(request):
    return render(request, "success.html")



@login_required
def appointment_history(request):
    try:
        patient = request.user.patient
        appointments = Appointment.objects.filter(
            patient=patient
        ).select_related("doctor", "patient").order_by("-date", "-time")
    except Patient.DoesNotExist:
         appointments = []

    return render(
        request,
        "appointment_history.html",
        {"appointments": appointments},
    )


def staff_required():
    return user_passes_test(
        lambda user: user.is_staff, login_url="/admin/login/"
    )


@staff_required()
def admin_dashboard(request):
    stats = {
        "doctors": Doctor.objects.count(),
        "patients": Patient.objects.count(),
        "appointments": Appointment.objects.count(),
        "pending": Appointment.objects.filter(
            status=Appointment.STATUS_PENDING
        ).count(),
    }
    appointments_by_status = (
        Appointment.objects.values("status").annotate(total=Count("id"))
    )
    recent_appointments = Appointment.objects.select_related("doctor", "patient")[:10]
    return render(
        request,
        "admin/dashboard.html",
        {
            "stats": stats,
            "appointments_by_status": appointments_by_status,
            "recent_appointments": recent_appointments,
        },
    )


@staff_required()
def admin_doctors(request):
    doctors = Doctor.objects.select_related("specialization").all()
    form = DoctorForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Doctor saved successfully.")
        return redirect("admin_doctors")
    return render(
        request,
        "admin/doctors.html",
        {"doctors": doctors, "form": form},
    )


@staff_required()
def admin_doctor_edit(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    form = DoctorForm(request.POST or None, instance=doctor)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Doctor updated successfully.")
        return redirect("admin_doctors")
    return render(
        request,
        "admin/doctor_form.html",
        {"form": form, "doctor": doctor},
    )


@staff_required()
def admin_doctor_delete(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    doctor.delete()
    messages.success(request, "Doctor removed.")
    return redirect("admin_doctors")


@staff_required()
def admin_specializations(request):
    form = SpecializationForm(request.POST or None)
    specializations = Specialization.objects.all()
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Specialization saved.")
        return redirect("admin_specializations")
    return render(
        request,
        "admin/specializations.html",
        {"form": form, "specializations": specializations},
    )


@staff_required()
def admin_specialization_detail(request, pk):
    specialization = get_object_or_404(Specialization, pk=pk)
    data = {
        "id": specialization.id,
        "name": specialization.name,
        "doctor_count": specialization.doctor_set.count(),
    }
    return JsonResponse(data)


@staff_required()
def admin_specialization_edit(request, pk):
    specialization = get_object_or_404(Specialization, pk=pk)
    # Handle JSON (AJAX) update
    if request.content_type == "application/json":
        try:
            import json

            payload = json.loads(request.body.decode("utf-8") or "{}")
            name = payload.get("name", "").strip()
            if not name:
                return JsonResponse({"error": "Name is required."}, status=400)
            specialization.name = name
            specialization.save()
            return JsonResponse({"id": specialization.id, "name": specialization.name})
        except Exception as exc:  # pragma: no cover - simplified error handling
            return JsonResponse({"error": str(exc)}, status=400)

    # Normal form-based edit
    form = SpecializationForm(request.POST or None, instance=specialization)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Specialization updated.")
        return redirect("admin_specializations")
    return render(
        request,
        "admin/specialization_form.html",
        {"form": form, "specialization": specialization},
    )


@staff_required()
def admin_specialization_delete(request, pk):
    if request.method != 'POST':
        return HttpResponseBadRequest('Invalid method')
    specialization = get_object_or_404(Specialization, pk=pk)
    # Set affected doctors' specialization to null and delete
    from .models import Doctor

    Doctor.objects.filter(specialization=specialization).update(specialization=None)
    specialization.delete()
    messages.success(request, "Specialization removed and assigned doctors cleared.")
    return redirect("admin_specializations")


@staff_required()
def admin_appointments(request):
    appointments = Appointment.objects.select_related("doctor", "patient")
    filter_form = AppointmentFilterForm(request.GET or None)
    if filter_form.is_valid():
        doctor = filter_form.cleaned_data.get("doctor")
        status = filter_form.cleaned_data.get("status")
        if doctor:
            appointments = appointments.filter(doctor=doctor)
        if status:
            appointments = appointments.filter(status=status)

    if request.method == "POST":
        appointment = get_object_or_404(Appointment, pk=request.POST.get("id"))
        status_form = AppointmentStatusForm(request.POST, instance=appointment)
        if status_form.is_valid():
            status_form.save()
            messages.success(request, "Appointment status updated.")
            params = request.GET.urlencode()
            redirect_url = reverse("admin_appointments")
            if params:
                redirect_url = f"{redirect_url}?{params}"
            return redirect(redirect_url)
        else:
            messages.error(request, "Invalid status update.")

    appointments = appointments.order_by("-date", "-time")
    status_form = AppointmentStatusForm()
    return render(
        request,
        "admin/appointments.html",
        {
            "appointments": appointments,
            "filter_form": filter_form,
            "status_form": status_form,
        },
    )
