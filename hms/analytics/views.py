from django.shortcuts import render
from django.db import models
from users.models import Appointment, PatientVitals

import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for web rendering
import matplotlib.pyplot as plt

import matplotlib.pyplot as plt
import io
import base64
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

def train_model():
    # Get all patient vitals from the database
    vitals = list(PatientVitals.objects.all().values('heart_rate', 'oxygen_level', 'blood_pressure', 'diagnosis'))

    if not vitals:  # Prevents error if no data is available
        return None  

    # 2. Convert to DataFrame
    df = pd.DataFrame(vitals)

    # 3. Preprocess Data
    df['blood_pressure'] = df['blood_pressure'].apply(lambda x: int(x.split('/')[0]))  # Take systolic BP
    df['diagnosis'] = df['diagnosis'].apply(lambda x: 1 if 'high risk' in x.lower() else 0)  # Binary classification

    # 4. Define Features (X) and Labels (y)
    X = df[['heart_rate', 'oxygen_level', 'blood_pressure']]
    y = df['diagnosis']

    # 5. Train a Simple ML Model (Logistic Regression)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = LogisticRegression()
    model.fit(X_train, y_train)

    return model

def analytics_dashboard(request):
    # Train the ML model
    model = train_model()

    # Get total appointments count
    total_appointments = Appointment.objects.count()
    completed_appointments = Appointment.objects.filter(status='completed').count()
    canceled_appointments = Appointment.objects.filter(status='canceled').count()

    # Get average patient vitals
    avg_heart_rate = PatientVitals.objects.aggregate(avg_heart_rate=models.Avg('heart_rate'))['avg_heart_rate'] or 0
    avg_oxygen = PatientVitals.objects.aggregate(avg_oxygen=models.Avg('oxygen_level'))['avg_oxygen'] or 0
    avg_blood_pressure = PatientVitals.objects.aggregate(avg_bp=models.Avg('blood_pressure'))['avg_bp'] or 0

    # Generate a graph using Matplotlib
    fig, ax = plt.subplots()
    categories = ['Total', 'Completed', 'Canceled']
    values = [total_appointments, completed_appointments, canceled_appointments]
    ax.bar(categories, values, color=['blue', 'green', 'red'])
    ax.set_title('Appointment Statistics')

    # Convert plot to image
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    chart_url = f'data:image/png;base64,{img}'

    # Predict Risk for a New Example Patient (Hardcoded example for now)
    risk_prediction = "Not Available"
    if model:
        new_patient = np.array([[80, 95, 120]])  # Example: 80 bpm, 95% oxygen, 120 BP
        risk_prediction = "High Risk" if model.predict(new_patient)[0] == 1 else "Low Risk"

    return render(request, 'analytics/analytics_dashboard.html', {
        'total_appointments': total_appointments,
        'completed_appointments': completed_appointments,
        'canceled_appointments': canceled_appointments,
        'avg_heart_rate': avg_heart_rate,
        'avg_oxygen': avg_oxygen,
        'avg_blood_pressure': avg_blood_pressure,
        'chart_url': chart_url,
        'risk_prediction': risk_prediction  # Send risk prediction to the template
    })