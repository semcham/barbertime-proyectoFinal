from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta, time, date

class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

class SoftDeleteModel(models.Model):
    is_active = models.BooleanField(default=True)

    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        self.is_active = False
        self.save()


class Cliente(SoftDeleteModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.user.first_name} ({self.phone})"

    def delete(self, *args, **kwargs):
        # Soft delete client record
        super().delete(*args, **kwargs)
        # Cancel client's upcoming scheduled appointments
        Appointment.objects.filter(client=self, status='SCHEDULED').update(status='CANCELLED')


class Service(SoftDeleteModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    duration = models.IntegerField()  # in minutes
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.name} ({self.duration} min - ${self.price})"

    def clean(self):
        if self.duration is not None and self.duration <= 0:
            raise ValidationError("La duración debe ser un número entero positivo.")
        if self.price is not None and self.price < 0:
            raise ValidationError("El precio no puede ser negativo.")


class Appointment(SoftDeleteModel):
    STATUS_CHOICES = [
        ('SCHEDULED', 'Programada'),
        ('COMPLETED', 'Completada'),
        ('CANCELLED', 'Cancelada'),
    ]

    client = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    barber = models.ForeignKey(User, on_delete=models.PROTECT)
    service = models.ForeignKey(Service, on_delete=models.PROTECT)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')

    def __str__(self):
        return f"Cita de {self.client.user.first_name} con {self.barber.first_name} - {self.date} {self.start_time}"

    def clean(self):
        # Require barber to be staff
        if self.barber and not self.barber.is_staff:
            raise ValidationError("El barbero seleccionado debe ser miembro del personal (staff).")

        # Require active service
        if self.service and not self.service.is_active:
            raise ValidationError("No se pueden programar citas para un servicio inactivo.")

        # Calculate end_time automatically if start_time and service are present
        if self.start_time and self.service:
            dummy_date = date(2000, 1, 1)
            start_dt = datetime.combine(dummy_date, self.start_time)
            end_dt = start_dt + timedelta(minutes=self.service.duration)
            self.end_time = end_dt.time()

        # Check operating hours (9:00 AM to 8:00 PM)
        if self.start_time and self.end_time:
            if self.start_time < time(9, 0) or self.end_time > time(20, 0):
                raise ValidationError("Las citas deben programarse dentro del horario laboral (9:00 AM - 8:00 PM).")

        # Check overlap
        if self.barber and self.date and self.start_time and self.end_time:
            overlapping = Appointment.objects.filter(
                barber=self.barber,
                date=self.date,
                is_active=True
            ).exclude(status='CANCELLED')

            if self.pk:
                overlapping = overlapping.exclude(pk=self.pk)

            for app in overlapping:
                # Standard overlap check
                if self.start_time < app.end_time and self.end_time > app.start_time:
                    raise ValidationError("El barbero ya tiene una cita programada en este horario.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
