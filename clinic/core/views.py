from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import (
    AppointmentFilterForm,
    AppointmentForm,
    AppointmentStatusForm,
    DoctorForm,
    SpecializationForm,
)
from .models import Appointment, Doctor, Patient, Specialization


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


def book_appointment(request):
    form = AppointmentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        patient, _ = Patient.objects.update_or_create(
            email=form.cleaned_data["email"],
            defaults={
                "name": form.cleaned_data["name"],
                "phone": form.cleaned_data["phone"],
            },
        )
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
    return render(
        request,
        "book_appointment.html",
        {"form": form, "doctors": Doctor.objects.all()},
    )


def appointment_success(request):
    return render(request, "success.html")


def appointment_history(request):
    appointments = None
    email = None
    if request.method == "POST":
        email = request.POST.get("email")
        if email:
            appointments = Appointment.objects.filter(
                patient__email=email
            ).select_related("doctor", "patient")
            if not appointments:
                messages.info(request, "No appointments found for the given email.")
        else:
            messages.error(request, "Please provide an email address.")
    return render(
        request,
        "appointment_history.html",
        {"appointments": appointments, "email": email},
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
