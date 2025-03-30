from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from .forms import CustomUserCreationForm, AppointmentForm, AppointmentStatusForm, AppointmentUpdateForm, AppointmentVitalsForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserChangeForm
from .decorators import role_required
from .models import Appointment, CustomUser

def home(request):
    return render(request, 'users/home.html')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in after signup
            return redirect('dashboard')  # Redirect to a dashboard page
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            # Redirect users based on their roles
            if user.role == 'admin':
                return redirect('admin_dashboard')
            elif user.role == 'doctor':
                return redirect('doctor_dashboard')
            elif user.role == 'staff':
                return redirect('staff_dashboard')
            else:  # Default is patient
                return redirect('patient_dashboard')

        else:
            return render(request, 'users/login.html', {'error': 'Invalid credentials'})
    return render(request, 'users/login.html')

def user_logout(request):
    logout(request)
    return redirect('login')  # Redirect to login page after logout

@login_required
def dashboard(request):
    if request.user.role == 'admin':
        return render(request, 'users/admin_dashboard.html')
    elif request.user.role == 'doctor':
        return render(request, 'users/doctor_dashboard.html')
    elif request.user.role == 'staff':
        return render(request, 'users/staff_dashboard.html')
    else:  # Default to patient dashboard
        return render(request, 'users/patient_dashboard.html')
    
@role_required(['admin'])
def admin_dashboard(request):
    if request.user.role != 'admin':  # Restrict access to only admins
        return redirect('login')  # Redirect non-admins to the login page

    users = CustomUser.objects.exclude(role='admin')  # Get all users except other admins
    appointments = Appointment.objects.all()  # Get all appointments

    return render(request, 'users/admin_dashboard.html', {
        'users': users,
        'appointments': appointments
    })

@login_required
@role_required(['doctor'])  # Only doctors can access
def doctor_dashboard(request):
    appointments = Appointment.objects.filter(doctor=request.user)  # Get doctor's appointments
    return render(request, 'users/doctor_dashboard.html', {'appointments': appointments})

@login_required
@role_required(['patient'])  # Only patients can access
def patient_dashboard(request):
    return render(request, 'users/patient_dashboard.html')

@login_required
def book_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user  # Assign logged-in user as the patient
            appointment.save()
            return redirect('patient_dashboard')  # Redirect to patient dashboard after booking
    else:
        form = AppointmentForm()
    
    return render(request, 'users/book_appointment.html', {'form': form})

@login_required
def patient_dashboard(request):
    appointments = Appointment.objects.filter(patient=request.user)  # Get patient’s appointments
    latest_vitals = appointments.filter(status='completed').order_by('-date', '-time').first()  # Get latest completed appointment with vitals

    return render(request, 'users/patient_dashboard.html', {
        'appointments': appointments,
        'latest_vitals': latest_vitals
    })

@login_required
def update_appointment_status(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user)  # Only allow doctor to update
    if request.method == 'POST':
        form = AppointmentStatusForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            return redirect('doctor_dashboard')  # Redirect back to doctor dashboard
    else:
        form = AppointmentStatusForm(instance=appointment)

    return render(request, 'users/update_appointment.html', {'form': form, 'appointment': appointment})

@login_required
def update_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user)  # ✅ Only assigned doctor can update
    if request.method == 'POST':
        form = AppointmentUpdateForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            return redirect('doctor_dashboard')  # ✅ Redirect back to doctor dashboard
    else:
        form = AppointmentUpdateForm(instance=appointment)

    return render(request, 'users/update_appointment.html', {'form': form, 'appointment': appointment})

@login_required
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Only allow the patient or doctor to cancel
    if request.user == appointment.patient or request.user == appointment.doctor:
        appointment.status = 'canceled'
        appointment.save()
        messages.success(request, "Appointment has been canceled.")
    else:
        messages.error(request, "You are not allowed to cancel this appointment.")

    # Redirect based on user role
    if request.user.role == 'doctor':
        return redirect('doctor_dashboard')
    return redirect('patient_dashboard')

@login_required
def add_vitals(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user)  # ✅ Only assigned doctor can update
    if request.method == 'POST':
        form = AppointmentVitalsForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            return redirect('doctor_dashboard')  # ✅ Redirect back to doctor dashboard
    else:
        form = AppointmentVitalsForm(instance=appointment)

    return render(request, 'users/add_vitals.html', {'form': form, 'appointment': appointment})

@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':  # ✅ Only allow admins
        return redirect('login')

    users = CustomUser.objects.exclude(role='admin')  # Exclude other admins
    appointments = Appointment.objects.all()  # Get all appointments

    return render(request, 'users/admin_dashboard.html', {
        'users': users,
        'appointments': appointments
    })

@login_required
def delete_user(request, user_id):
    if request.user.role != 'admin':  # Only admins can delete users
        return redirect('admin_dashboard')

    user = get_object_or_404(CustomUser, id=user_id)

    if user.role == 'admin':  # Prevent deleting other admins
        messages.error(request, "You cannot delete an admin user.")
        return redirect('admin_dashboard')

    user.delete()
    messages.success(request, "User deleted successfully.")
    return redirect('admin_dashboard')

@login_required
def edit_appointment(request, appointment_id):
    if request.user.role != 'admin':  # ✅ Only admins can edit appointments
        return redirect('admin_dashboard')

    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.method == 'POST':
        form = AppointmentUpdateForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, "Appointment updated successfully.")
            return redirect('admin_dashboard')
    else:
        form = AppointmentUpdateForm(instance=appointment)

    return render(request, 'users/edit_appointment.html', {'form': form, 'appointment': appointment})

@login_required
def edit_user(request, user_id):
    if request.user.role != 'admin':  # ✅ Only admins can edit users
        return redirect('admin_dashboard')

    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "User details updated successfully.")
            return redirect('admin_dashboard')
    else:
        form = UserChangeForm(instance=user)

    return render(request, 'users/edit_user.html', {'form': form, 'user': user})