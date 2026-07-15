from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Cliente, Service, Appointment
from datetime import date

class ClientRegistrationForm(forms.Form):
    name = forms.CharField(
        max_length=150,
        label="Nombre Completo",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Juan Pérez'})
    )
    phone = forms.CharField(
        max_length=20,
        label="Número de Teléfono",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. 3001234567'})
    )
    email = forms.EmailField(
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'tucorreo@ejemplo.com'})
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña (mín. 8 caracteres)'})
    )

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.isdigit():
            raise ValidationError("El número de teléfono debe contener solo dígitos.")
        if len(phone) < 7 or len(phone) > 15:
            raise ValidationError("El número de teléfono debe tener entre 7 y 15 dígitos.")
        if User.objects.filter(username=phone).exists():
            raise ValidationError("El número de teléfono ya está registrado.")
        return phone

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Cliente.objects.filter(email=email).exists():
            raise ValidationError("Ese correo electrónico ya está registrado.")
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres.")
        return password

class ClientAppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['service', 'barber', 'date', 'start_time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'service': forms.Select(attrs={'class': 'form-control'}),
            'barber': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit querysets to active objects
        self.fields['service'].queryset = Service.objects.filter(is_active=True)
        self.fields['barber'].queryset = User.objects.filter(is_staff=True, is_active=True)
        
        # Style labels
        self.fields['service'].label = "Servicio"
        self.fields['barber'].label = "Barbero"
        self.fields['date'].label = "Fecha"
        self.fields['start_time'].label = "Hora de Inicio"

    def clean_date(self):
        booking_date = self.cleaned_data.get('date')
        if booking_date and booking_date < date.today():
            raise ValidationError("No se pueden reservar citas en fechas pasadas.")
        return booking_date

    def clean(self):
        cleaned_data = super().clean()
        service = cleaned_data.get('service')
        barber = cleaned_data.get('barber')
        booking_date = cleaned_data.get('date')
        start_time = cleaned_data.get('start_time')

        if service and barber and booking_date and start_time:
            # We don't have client here, so we build a dummy or handle in view, 
            # but we can do a mock validation here or leave it to the model save validation.
            # However, since model clean checks overlap, we will perform a model validation check.
            pass
        return cleaned_data


class AdminAppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['client', 'service', 'barber', 'date', 'start_time', 'status']
        widgets = {
            'client': forms.Select(attrs={'class': 'form-control'}),
            'service': forms.Select(attrs={'class': 'form-control'}),
            'barber': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['client'].queryset = Cliente.objects.filter(is_active=True)
        self.fields['service'].queryset = Service.objects.filter(is_active=True)
        self.fields['barber'].queryset = User.objects.filter(is_staff=True, is_active=True)
        
        self.fields['client'].label = "Cliente"
        self.fields['service'].label = "Servicio"
        self.fields['barber'].label = "Barbero"
        self.fields['date'].label = "Fecha"
        self.fields['start_time'].label = "Hora de Inicio"
        self.fields['status'].label = "Estado"
