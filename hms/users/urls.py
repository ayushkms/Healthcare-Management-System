from django.urls import path
from .views import home, register, user_login, user_logout, dashboard, admin_dashboard, doctor_dashboard, patient_dashboard, book_appointment, update_appointment_status, update_appointment, cancel_appointment, add_vitals, delete_user, edit_appointment, edit_user

urlpatterns = [

    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('doctor-dashboard/', doctor_dashboard, name='doctor_dashboard'),  # Doctor Dashboard
    path('patient-dashboard/', patient_dashboard, name='patient_dashboard'),
    path('book-appointment/', book_appointment, name='book_appointment'),
    path('update-appointment/<int:appointment_id>/', update_appointment_status, name='update_appointment_status'),
    path('update-appointment/<int:appointment_id>/', update_appointment, name='update_appointment'),
    path('cancel-appointment/<int:appointment_id>/', cancel_appointment, name='cancel_appointment'),
    path('add-vitals/<int:appointment_id>/', add_vitals, name='add_vitals'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('delete-user/<int:user_id>/', delete_user, name='delete_user'),
    path('edit-appointment/<int:appointment_id>/', edit_appointment, name='edit_appointment'),
    path('edit-user/<int:user_id>/', edit_user, name='edit_user'),
]