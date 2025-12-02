from django.db import models


class Specialization(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Doctor(models.Model):
    name = models.CharField(max_length=200)
    specialization = models.ForeignKey(Specialization, on_delete=models.CASCADE)
    experience = models.IntegerField(help_text="Experience in years")
    fees = models.IntegerField(help_text="Consultation fees in local currency")
    available_days = models.CharField(
        max_length=200,
        help_text="Comma separated days e.g. Mon,Tue,Fri",
    )
    time_slots = models.CharField(
        max_length=300,
        help_text="Comma separated time slots e.g. 10:00 AM,11:30 AM",
    )
    biography = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def day_list(self):
        return [day.strip() for day in self.available_days.split(",") if day.strip()]

    @property
    def slot_list(self):
        return [slot.strip() for slot in self.time_slots.split(",") if slot.strip()]


class Patient(models.Model):
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Appointment(models.Model):
    STATUS_PENDING = "Pending"
    STATUS_APPROVED = "Approved"
    STATUS_COMPLETED = "Completed"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_COMPLETED, "Completed"),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.CharField(max_length=50)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-time"]
        unique_together = ("doctor", "date", "time")

    def __str__(self):
        return f"{self.patient.name} - {self.doctor.name}"
