from django.contrib import admin
from .models import Cliente, Service, Appointment

# Registro de tus modelos en el panel de control
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration', 'price', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'email', 'is_active')
    search_fields = ('user__first_name', 'user__last_name', 'phone', 'email')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('client', 'barber', 'service', 'date', 'start_time', 'end_time', 'status')
    list_filter = ('status', 'date', 'barber')
    search_fields = ('client__user__first_name', 'barber__first_name')

# Register your models here.
