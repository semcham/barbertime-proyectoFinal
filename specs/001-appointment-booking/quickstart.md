# Quickstart & Validation Guide: Appointment Booking System

This guide outlines the environment setup, local verification commands, and end-to-end validation scenarios for testing the BarberTime Appointment Booking System.

---

## 1. Prerequisites & Setup

Ensure Python 3.11+ and PostgreSQL are installed locally.

### Step 1: Environment Configuration
Create a `.env` file in the project root:
```ini
DEBUG=True
SECRET_KEY=local-dev-secret-key-12345
DATABASE_URL=postgres://postgres:postgres@localhost:5432/barbertime
```

### Step 2: Dependency Installation
Create a virtual environment and install the required stack (as researched in [research.md](file:///D:/barbertime-proyectoFinal/specs/001-appointment-booking/research.md)):
```bash
python -m venv venv
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate

pip install Django dj-database-url psycopg2-binary gunicorn whitenoise
```

### Step 3: Database Initialization
Apply migrations and create the first administrative (Staff) user:
```bash
python manage.py migrate
python manage.py createsuperuser
```
*(Ensure to mark `is_staff=True` on any user representing a Barber in the database).*

### Step 4: Run Server
Start the local Django server:
```bash
python manage.py runserver
```

---

## 2. End-to-End Validation Scenarios

### Scenario 1: Client Registration and Login Flow
- **Goal**: Verify a client can self-register with their phone number and log in.
- **Actions**:
  1. Open a browser and navigate to `http://127.0.0.1:8000/register/`.
  2. Input name: `John Doe`, phone: `555123456`, password: `Password123`. Submit.
  3. Verify you are automatically redirected to `http://127.0.0.1:8000/dashboard/`.
  4. Log out, then navigate to `http://127.0.0.1:8000/login/`.
  5. Log in using phone `555123456` and password `Password123`.

### Scenario 2: Double-Booking Overlap Prevention
- **Goal**: Confirm the system blocks overlapping bookings for the same barber.
- **Prerequisites**: One active Barber (e.g., Staff User ID: `2`) and one active Service (e.g., ID: `1`, duration: 30 minutes).
- **Actions**:
  1. Login as client `John Doe` and navigate to `/book/`.
  2. Book Barber `2` for Service `1` at date `2026-07-15` starting at `10:00 AM`. Confirm booking (ends at `10:30 AM`).
  3. Register/login as another client `Jane Smith`.
  4. Navigate to `/book/` and attempt to book Barber `2` for Service `1` on `2026-07-15` at `10:15 AM`.
  5. **Expected Outcome**: The booking is rejected with a validation message: *"The selected barber is already booked during this time interval."*

### Scenario 3: Data Isolation & Privacy Verification
- **Goal**: Ensure a client cannot view or cancel other clients' appointments.
- **Actions**:
  1. Login as client `Jane Smith`.
  2. Attempt to directly access `http://127.0.0.1:8000/appointments/<john_does_appointment_id>/cancel/` via a POST request or URL manipulation.
  3. **Expected Outcome**: The system returns a `404 Not Found` or `403 Forbidden` response.
  4. Verify that Jane Smith's dashboard only lists appointments linked to her user profile.

### Scenario 4: Admin Filtering & Scheduling on Behalf
- **Goal**: Verify staff can filter all appointments and book on behalf of any client.
- **Actions**:
  1. Log in to the administrator portal at `http://127.0.0.1:8000/admin-dashboard/`.
  2. Select filter `Date: 2026-07-15` and `Status: Scheduled`. Verify only John Doe's booking appears.
  3. Click "Book on Behalf", select Client: `Jane Smith`, Barber: `2`, Service: `1`, Date: `2026-07-15`, Time: `11:00 AM`. Confirm.
  4. Verify the booking appears on the dashboard and is linked to Jane Smith.

### Scenario 5: Soft-Deletion Audit
- **Goal**: Verify cancellations perform a logical delete (not physical delete) per [data-model.md](file:///D:/barbertime-proyectoFinal/specs/001-appointment-booking/data-model.md).
- **Actions**:
  1. Log in as client `John Doe`.
  2. Click "Cancel" on the `10:00 AM` booking. Confirm cancellation.
  3. Open Python interactive shell:
     ```bash
     python manage.py shell
     ```
  4. Execute query:
     ```python
     from myapp.models import Appointment
     # Verify it does NOT appear in default active queries
     print(Appointment.objects.filter(id=john_does_appointment_id).exists()) # Expected: False
     # Verify it exists in all objects (deleted audit)
     print(Appointment.all_objects.filter(id=john_does_appointment_id).exists()) # Expected: True
     ```
