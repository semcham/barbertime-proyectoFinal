from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from appointments.models import Cliente, Service, Appointment

class AuthenticationTests(TestCase):
    def test_client_registration_success(self):
        response = self.client.post(reverse('register'), {
            'name': 'Test Client',
            'phone': '1234567890',
            'email': 'test.client@test.com',
            'password': 'securepassword123'
        })
        self.assertRedirects(response, reverse('dashboard'))
        
        user = User.objects.get(username='1234567890')
        self.assertEqual(user.first_name, 'Test Client')
        self.assertTrue(hasattr(user, 'cliente'))
        self.assertTrue(user.cliente.is_active)

    def test_client_registration_duplicate_phone(self):
        User.objects.create_user(username='1234567890', password='password123')
        
        response = self.client.post(reverse('register'), {
            'name': 'Another Client',
            'phone': '1234567890',
            'email': 'otro.cliente@test.com',
            'password': 'securepassword123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'El número de teléfono ya está registrado')

    def test_client_login_success(self):
        user = User.objects.create_user(username='1234567890', password='password123')
        Cliente.objects.create(user=user, phone='1234567890', email='login.test@test.com')
        
        response = self.client.post(reverse('login'), {
            'username': '1234567890',
            'password': 'password123'
        })
        self.assertRedirects(response, reverse('dashboard'))

    def test_staff_login_redirects_to_admin_dashboard(self):
        User.objects.create_superuser(username='admin', password='adminpassword')
        
        response = self.client.post(reverse('login'), {
            'username': 'admin',
            'password': 'adminpassword'
        })
        self.assertRedirects(response, reverse('admin_dashboard'))


class ClientPortalTests(TestCase):
    def setUp(self):
        self.client_user1 = User.objects.create_user(username='1111111111', password='password123')
        self.client1 = Cliente.objects.create(user=self.client_user1, phone='1111111111', email='portal.uno@test.com')
        
        self.client_user2 = User.objects.create_user(username='2222222222', password='password123')
        self.client2 = Cliente.objects.create(user=self.client_user2, phone='2222222222', email='portal.dos@test.com')
        
        self.barber = User.objects.create_user(username='barber1', password='password123', is_staff=True)
        self.service = Service.objects.create(name='Corte', duration=30, price=15.00)
        
        self.app1 = Appointment.objects.create(
            client=self.client1,
            barber=self.barber,
            service=self.service,
            date='2026-07-15',
            start_time='10:00:00',
            end_time='10:30:00'
        )

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('dashboard')}")

    def test_client_only_sees_own_appointments(self):
        self.client.login(username='1111111111', password='password123')
        response = self.client.get(reverse('dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Corte')
        self.assertContains(response, '10:00')
        
        self.client.logout()
        self.client.login(username='2222222222', password='password123')
        response = self.client.get(reverse('dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '10:00')

    def test_client_cannot_cancel_others_appointment(self):
        self.client.login(username='2222222222', password='password123')
        response = self.client.post(reverse('cancel_appointment', args=[self.app1.id]))
        self.assertEqual(response.status_code, 404)
        
        self.app1.refresh_from_db()
        self.assertEqual(self.app1.status, 'SCHEDULED')
