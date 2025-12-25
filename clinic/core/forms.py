from django import forms

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Appointment, Doctor, Specialization, Patient


class AppointmentForm(forms.Form):
    name = forms.CharField(max_length=200)
    phone = forms.CharField(max_length=20)
    email = forms.EmailField()
    doctor = forms.ModelChoiceField(queryset=Doctor.objects.all())
    date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    time = forms.CharField(max_length=50)
    notes = forms.CharField(widget=forms.Textarea, required=False)

    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get("doctor")
        time = cleaned_data.get("time", "").strip()
        date = cleaned_data.get("date")

        if doctor and date and time:
            exists = Appointment.objects.filter(
                doctor=doctor, date=date, time=time
            ).exists()
            if exists:
                raise forms.ValidationError(
                    "This slot has already been booked for the chosen doctor."
                )
        return cleaned_data


class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = [
            "name",
            "specialization",
            "experience",
            "fees",
            "available_days",
            "time_slots",
            "biography",
        ]
        widgets = {
            "biography": forms.Textarea(attrs={"rows": 4}),
        }


class SpecializationForm(forms.ModelForm):
    class Meta:
        model = Specialization
        fields = ["name"]


class AppointmentStatusForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["status"]


class AppointmentFilterForm(forms.Form):
    doctor = forms.ModelChoiceField(
        queryset=Doctor.objects.all(),
        required=False,
        empty_label="All doctors",
    )
    status = forms.ChoiceField(
        choices=[("", "All statuses")] + list(Appointment.STATUS_CHOICES),
        required=False,
    )



class PatientSignupForm(UserCreationForm):
    name = forms.CharField(max_length=200, required=True, help_text="Full access name")
    phone = forms.CharField(max_length=20, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "name", "phone")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            Patient.objects.create(
                user=user,
                name=self.cleaned_data["name"],
                phone=self.cleaned_data["phone"],
                email=self.cleaned_data["email"],
            )
        return user
