from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from appointments.models import Cliente, Service, Appointment

class ModelSoftDeleteTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='1234567890', password='password123')
        self.client_profile = Cliente.objects.create(user=self.user, phone='1234567890')
        self.service = Service.objects.create(name='Corte de Cabello', duration=30, price=15.00)

    def test_soft_delete_hides_record_by_default(self):
        self.assertEqual(Cliente.objects.count(), 1)
        self.assertEqual(Service.objects.count(), 1)
        
        # Soft delete
        self.client_profile.delete()
        self.service.delete()
        
        # objects manager should filter them out
        self.assertEqual(Cliente.objects.count(), 0)
        self.assertEqual(Service.objects.count(), 0)
        
        # all_objects manager should still return them
        self.assertEqual(Cliente.all_objects.count(), 1)
        self.assertEqual(Service.all_objects.count(), 1)
        
        # Check active flag
        self.assertFalse(Cliente.all_objects.first().is_active)
        self.assertFalse(Service.all_objects.first().is_active)


class AppointmentOverlapTests(TestCase):
    def setUp(self):
        self.client_user1 = User.objects.create_user(username='1111111111', password='password123')
        self.client1 = Cliente.objects.create(user=self.client_user1, phone='1111111111')
        
        self.client_user2 = User.objects.create_user(username='2222222222', password='password123')
        self.client2 = Cliente.objects.create(user=self.client_user2, phone='2222222222')
        
        self.barber = User.objects.create_user(username='barber1', password='password123', is_staff=True)
        
        self.service_short = Service.objects.create(name='Corte', duration=30, price=10.00)
        self.service_long = Service.objects.create(name='Corte y Barba', duration=60, price=20.00)
        
        # Base appointment on 2026-07-15 from 10:00 to 10:30
        self.app1 = Appointment(
            client=self.client1,
            barber=self.barber,
            service=self.service_short,
            date='2026-07-15',
            start_time='10:00:00'
        )
        self.app1.save()

    def test_overlap_exact_same_time_rejected(self):
        # Attempt to book exact same time
        app_overlap = Appointment(
            client=self.client2,
            barber=self.barber,
            service=self.service_short,
            date='2026-07-15',
            start_time='10:00:00'
        )
        with self.assertRaises(ValidationError):
            app_overlap.clean()

    def test_overlap_partial_overlap_rejected(self):
        # Starts inside app1 (10:00 - 10:30)
        app_overlap = Appointment(
            client=self.client2,
            barber=self.barber,
            service=self.service_short,
            date='2026-07-15',
            start_time='10:15:00'
        )
        with self.assertRaises(ValidationError):
            app_overlap.clean()

    def test_no_overlap_immediately_after_allowed(self):
        # Starts right when app1 ends
        app_no_overlap = Appointment(
            client=self.client2,
            barber=self.barber,
            service=self.service_short,
            date='2026-07-15',
            start_time='10:30:00'
        )
        try:
            app_no_overlap.clean()
        except ValidationError:
            self.fail("ValidationError raised on non-overlapping adjacent appointment.")

    def test_overlap_cancelled_appointment_allowed(self):
        self.app1.status = 'CANCELLED'
        self.app1.save()
        
        app_ok = Appointment(
            client=self.client2,
            barber=self.barber,
            service=self.service_short,
            date='2026-07-15',
            start_time='10:15:00'
        )
        try:
            app_ok.clean()
        except ValidationError:
            self.fail("ValidationError raised on overlapping with a cancelled appointment.")


class CascadeDeactivationTests(TestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(username='1111111111', password='password123')
        self.client = Cliente.objects.create(user=self.client_user, phone='1111111111')
        self.barber = User.objects.create_user(username='barber1', password='password123', is_staff=True)
        self.service = Service.objects.create(name='Corte', duration=30, price=10.00)
        
        self.app1 = Appointment.objects.create(
            client=self.client,
            barber=self.barber,
            service=self.service,
            date='2026-07-15',
            start_time='10:00:00'
        )

    def test_client_deactivation_cancels_future_appointments(self):
        self.assertEqual(self.app1.status, 'SCHEDULED')
        
        # Soft delete the client
        self.client.delete()
        
        # Reload appointment
        self.app1.refresh_from_db()
        self.assertEqual(self.app1.status, 'CANCELLED')
