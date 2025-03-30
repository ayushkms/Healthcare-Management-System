from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Appointment

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'role']

class AppointmentForm(forms.ModelForm):
    doctor = forms.ModelChoiceField(queryset=CustomUser.objects.filter(role='doctor'), label="Select Doctor")

    class Meta:
        model = Appointment
        fields = ['doctor', 'date', 'time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }

class AppointmentStatusForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['status']

class AppointmentUpdateForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['status']
        widgets = {
            'status': forms.Select(choices=[
                ('pending', 'Pending'),
                ('confirmed', 'Confirmed'),
                ('completed', 'Completed')
            ])
        }

class AppointmentVitalsForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['heart_rate', 'oxygen_level', 'blood_pressure', 'height', 'weight', 'diagnosis']

class AppointmentUpdateForm(forms.ModelForm):
    doctor = forms.ModelChoiceField(queryset=CustomUser.objects.filter(role='doctor'), label="Reassign Doctor")

    class Meta:
        model = Appointment
        fields = ['doctor', 'date', 'time', 'status']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }