# Web Endpoints Contract: Appointment Booking System

This contract documents the URL structure, access controls, HTTP methods, form payloads, and rendering behaviors for the BarberTime server-rendered web interface.

---

## Access Control Roles
- **Anonymous**: Unauthenticated web visitors.
- **Client**: Authenticated users who have `is_staff=False`.
- **Staff**: Authenticated users who have `is_staff=True` (Administrators/Barbers).

---

## 1. Authentication & Registration Endpoints

### `POST /register/`
- **Access**: Anonymous
- **Purpose**: Self-registration for clients.
- **Form Payload**:
  - `name`: string (Required)
  - `phone`: string (Required, must be unique, format validated for 9-10 digits)
  - `password`: string (Required, min 8 characters)
- **Behavior**:
  - **Success**: Creates a `User` (username=phone) and a linked `Cliente`. Logs in the user session and redirects to `GET /dashboard/`.
  - **Failure**: Re-renders the registration page with error messages (e.g. if phone number already registered).

### `GET /login/`
- **Access**: Anonymous (Redirects to dashboard if logged in)
- **Purpose**: Render the login form.
- **Template**: `registration/login.html`

### `POST /login/`
- **Access**: Anonymous
- **Purpose**: Authenticate user and initiate session.
- **Form Payload**:
  - `username`: string (Phone number for clients, username for staff)
  - `password`: string (Required)
- **Behavior**:
  - **Success (Client)**: Redirects to `GET /dashboard/`.
  - **Success (Staff)**: Redirects to `GET /admin-dashboard/`.
  - **Failure**: Re-renders login page with invalid credentials error.

### `POST /logout/`
- **Access**: Client, Staff
- **Purpose**: Terminate session.
- **Behavior**: Destroys session and redirects to `GET /login/`.

---

## 2. Client Portal Endpoints

### `GET /dashboard/`
- **Access**: Client (Redirects to login if unauthenticated or staff)
- **Purpose**: Display client's profile and list of only their own appointments.
- **Template**: `client/dashboard.html`
- **Context Variables**:
  - `client`: `Cliente` instance
  - `upcoming_appointments`: QuerySet of active appointments in `SCHEDULED` status.
  - `past_appointments`: QuerySet of appointments in `COMPLETED` or `CANCELLED` status.

### `GET /book/`
- **Access**: Client
- **Purpose**: Render the appointment booking form.
- **Template**: `client/book.html`
- **Context Variables**:
  - `services`: QuerySet of active `Service` instances.
  - `barbers`: QuerySet of active Staff `User` instances.

### `POST /book/`
- **Access**: Client
- **Purpose**: Create a new appointment for the logged-in client.
- **Form Payload**:
  - `service_id`: integer (Required, FK to Service)
  - `barber_id`: integer (Required, FK to Staff User)
  - `date`: date (Required, YYYY-MM-DD, must be today or future)
  - `start_time`: time (Required, HH:MM, within operating hours)
- **Behavior**:
  - **Success**: Saves the new appointment and redirects to `GET /dashboard/`.
  - **Failure**: Re-renders `client/book.html` displaying validation errors (e.g., barber overlap, out of operating hours).

### `POST /appointments/<int:id>/cancel/`
- **Access**: Client (Owner only)
- **Purpose**: Soft-cancel an upcoming appointment.
- **Behavior**:
  - Validates that the appointment belongs to the logged-in user and status is `SCHEDULED`.
  - **Success**: Sets status to `'CANCELLED'` and redirects to `GET /dashboard/`.
  - **Failure**: Returns 404 (if not owned/found) or 400 Bad Request.

---

## 3. Administrative Portal Endpoints

### `GET /admin-dashboard/`
- **Access**: Staff (Redirects to login if unauthenticated or non-staff)
- **Purpose**: Master list of all system appointments.
- **Template**: `admin/dashboard.html`
- **Query Parameters (Filters)**:
  - `date`: date (Optional, YYYY-MM-DD, defaults to current date)
  - `status`: string (Optional, choices: `SCHEDULED`, `COMPLETED`, `CANCELLED`, `ALL`. Defaults to `ALL`)
- **Context Variables**:
  - `appointments`: Filtered list of appointments.
  - `selected_date`: Date string.
  - `selected_status`: Status string.

### `GET /admin/appointments/book/`
- **Access**: Staff
- **Purpose**: Render booking form to book on behalf of any client.
- **Template**: `admin/book_appointment.html`
- **Context Variables**:
  - `clients`: QuerySet of active `Cliente` instances.
  - `services`: QuerySet of active `Service` instances.
  - `barbers`: QuerySet of active Staff `User` instances.

### `POST /admin/appointments/book/`
- **Access**: Staff
- **Purpose**: Create an appointment on behalf of a selected client.
- **Form Payload**:
  - `client_id`: integer (Required, FK to Cliente)
  - `service_id`: integer (Required, FK to Service)
  - `barber_id`: integer (Required, FK to Staff User)
  - `date`: date (Required, YYYY-MM-DD)
  - `start_time`: time (Required, HH:MM)
- **Behavior**:
  - **Success**: Creates appointment and redirects to `GET /admin-dashboard/`.
  - **Failure**: Re-renders form with validation/conflict errors.

### `POST /admin/appointments/<int:id>/status/`
- **Access**: Staff
- **Purpose**: Update status or deactivate an appointment.
- **Form Payload**:
  - `status`: string (`SCHEDULED`, `COMPLETED`, `CANCELLED`)
  - `is_active`: boolean (Optional, to trigger soft delete)
- **Behavior**:
  - **Success**: Updates appointment status/activity and redirects to `GET /admin-dashboard/`.
