from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='patient')

    def __str__(self):
        return self.username

class Appointment(models.Model):
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='doctor_appointments')
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(
        max_length=10, 
        choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('completed', 'Completed'), ('canceled', 'Canceled')], 
        default='pending'
    )

    # Fields for patient vitals
    heart_rate = models.IntegerField(null=True, blank=True)
    oxygen_level = models.IntegerField(null=True, blank=True)
    blood_pressure = models.CharField(max_length=20, null=True, blank=True)
    height = models.FloatField(null=True, blank=True)  # In cm
    weight = models.FloatField(null=True, blank=True)  # In kg
    diagnosis = models.CharField(max_length=255, null=True, blank=True)  # Disease name


    def __str__(self):
        return f"Appointment with Dr. {self.doctor.username} on {self.date} at {self.time}"

class PatientVitals(models.Model):
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # ✅ Correct reference
    heart_rate = models.IntegerField()
    oxygen_level = models.FloatField()
    blood_pressure = models.CharField(max_length=20)
    height = models.FloatField()
    weight = models.FloatField()
    diagnosis = models.CharField(max_length=255)
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Vitals for {self.patient.username} - {self.recorded_at}"