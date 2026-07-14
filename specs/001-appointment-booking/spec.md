# Feature Specification: Appointment Booking System

**Feature Branch**: `001-appointment-booking`

**Created**: 2026-07-14

**Status**: Draft

**Input**: User description: "Sistema web de reservas de citas para BarberTime, una barbería. Tiene dos partes: (1) Panel de administrador: el personal (staff) inicia sesión y gestiona clientes, servicios y citas de cualquier persona, viendo el listado completo de citas con filtros por fecha y estado. (2) Portal de clientes: cualquier persona se registra ella misma con su nombre, teléfono y contraseña, inicia sesión, y reserva su propia cita eligiendo servicio, barbero y horario disponible, viendo únicamente sus propias citas (no las de otros clientes) y pudiendo cancelarlas. El sistema debe validar automáticamente que no haya cruces de horario para un mismo barbero, tanto cuando reserva el administrador como cuando reserva el cliente."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Client Registration & Authentication (Priority: P1)

Any new customer can register by providing their name, phone number, and a secure password. Once registered, they can log in to access the client portal.

**Why this priority**: Crucial entry point to enable personalized experience and ensure customer privacy.

**Independent Test**: A new user can successfully sign up and log in, seeing an empty upcoming appointments dashboard.

**Acceptance Scenarios**:

1. **Given** a visitor is on the registration page, **When** they fill in their name, a unique phone number, and a secure password and submit the form, **Then** their client account is created, they are automatically logged in, and they are redirected to the client dashboard.
2. **Given** a registered client is on the login page, **When** they enter their phone number and correct password, **Then** they are logged in and redirected to the client dashboard.
3. **Given** a visitor tries to register, **When** they enter a phone number that is already registered in the system, **Then** the registration fails with a clear message indicating the phone number is already in use.

---

### User Story 2 - Client Booking & Appointment Management (Priority: P1)

An authenticated client can book their own appointment by choosing a service, a barber, and an available date and time. They can view a list of only their own appointments and cancel any upcoming appointments.

**Why this priority**: Core value proposition for clients, allowing them to schedule and manage their visits.

**Independent Test**: An authenticated client can schedule a haircut with a selected barber, see it on their dashboard, and cancel it, freeing up that time slot.

**Acceptance Scenarios**:

1. **Given** an authenticated client is booking an appointment, **When** they select a service, a barber, and an available date and time slot, **Then** the appointment is created and listed on their dashboard as "Scheduled".
2. **Given** an authenticated client is on their dashboard, **When** they view their appointment history or upcoming list, **Then** they see only their own appointments, with no access to or visibility of other clients' details or bookings.
3. **Given** a client has an upcoming appointment in the "Scheduled" state, **When** they click "Cancel" and confirm, **Then** the appointment status changes to "Cancelled", and the barber's time slot becomes immediately available for other bookings.

---

### User Story 3 - Admin Management of Clients, Services, and Appointments (Priority: P2)

Staff members (admin/barbers) can log in to a dedicated administrative panel to manage client profiles, service offerings, and book/edit/cancel appointments for any client.

**Why this priority**: Allows business staff to manage overall operations, assist clients who book over the phone, and configure the services offered.

**Independent Test**: An administrator can log in, add a new service (e.g., "Beard Trim"), search for a client, and book an appointment for that client.

**Acceptance Scenarios**:

1. **Given** an authenticated staff member is in the admin panel, **When** they view the clients list, **Then** they can create new client profiles, edit details, or mark a client as inactive (logical deletion).
2. **Given** an authenticated staff member is managing services, **When** they create, edit, or deactivate a service, **Then** the service list is updated, and deactivated services are hidden from new client bookings but remain in historical records.
3. **Given** an authenticated staff member, **When** they create or edit an appointment for any client, **Then** the system validates availability, saves the booking, and displays it on the central administrative schedule.

---

### User Story 4 - Automatic Schedule Conflict Prevention (Priority: P1)

The system automatically validates that a barber cannot be double-booked. No two active appointments for the same barber can overlap in time, whether booked by a client or an administrator.

**Why this priority**: Critical business logic to prevent scheduling errors and ensure smooth operations.

**Independent Test**: Attempt to book an appointment with Barber X that overlaps with Barber X's existing appointment and verify the booking is rejected.

**Acceptance Scenarios**:

1. **Given** Barber A has a scheduled appointment from 10:00 AM to 10:45 AM, **When** a client or administrator attempts to book a new appointment for Barber A starting at 10:30 AM, **Then** the system rejects the booking and displays a validation error stating the barber is unavailable.
2. **Given** Barber A has a scheduled appointment from 10:00 AM to 10:45 AM, **When** a booking is requested for Barber A starting at 10:45 AM or later, **Then** the booking is successfully confirmed.
3. **Given** Barber A has a scheduled appointment that is subsequently "Cancelled", **When** a new appointment is requested for Barber A during that same time slot, **Then** the booking is successfully confirmed.

---

### User Story 5 - Admin Appointment Dashboard and Filtering (Priority: P2)

Administrators can view a master list of all appointments in the system, with filters to quickly search by date and appointment status.

**Why this priority**: Essential for daily barber shop operations, allowing staff to view the day's schedule and track cancellations.

**Independent Test**: An admin filters the master list for a specific date and "Scheduled" status, returning only active appointments for that day.

**Acceptance Scenarios**:

1. **Given** an administrator is on the dashboard list view, **When** they select a specific date filter, **Then** the list dynamically updates to show only appointments scheduled for that date.
2. **Given** an administrator is on the dashboard list view, **When** they filter by status (e.g., "Cancelled"), **Then** only appointments with the "Cancelled" status are shown.

---

### Edge Cases

- **Service Deactivation**: When a service is logically deleted (marked inactive), any existing scheduled appointments for that service must remain active and visible. However, no new appointments can be booked for that service.
- **Client Deactivation**: When a client profile is marked inactive, their future scheduled appointments should be automatically cancelled to free up the barbers' calendars.
- **Race Condition Bookings**: If two users attempt to book the exact same time slot for the same barber simultaneously, the transaction must be handled sequentially. The first booking request processed must succeed, and the second must fail with a validation message indicating the slot has just been taken.
- **Out of Hours Booking**: If a booking is requested outside standard operating hours (e.g., 9:00 PM), the system must reject it.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST support client self-registration with name, unique phone number, and password, and secure login for both clients and staff.
- **FR-002**: Clients MUST only be able to view, search, and cancel their own appointments, ensuring complete isolation from other clients' data.
- **FR-003**: Staff members MUST be able to manage (create, view, edit, logically delete) clients, services, and appointments for any customer.
- **FR-004**: The system MUST automatically validate schedule conflicts for the chosen barber. An appointment booking MUST be rejected if the start-to-end interval overlaps with any other active (non-cancelled) appointment for the same barber.
- **FR-005**: The system MUST implement logical deletion (soft delete) for clients, services, and appointments by setting an active/inactive status flag rather than permanently deleting database rows.
- **FR-006**: The admin panel MUST display a list of all appointments with filters for date (single day) and appointment status (e.g., Scheduled, Completed, Cancelled).

### Key Entities *(include if feature involves data)*

- **Client**: Represents a registered customer. Key attributes: Name, Phone Number, Password (secured/hashed), Active Status (Boolean).
- **Staff/Admin**: Represents a barber shop employee or system administrator who can log in to the admin panel. Key attributes: Username, Password, Active Status (Boolean).
- **Barber**: Represents a service provider (may map directly to a Staff/Admin user who performs services). Key attributes: Name, Active Status (Boolean).
- **Service**: Represents a haircut, shave, or other styling service. Key attributes: Name, Description, Duration (minutes), Price, Active Status (Boolean).
- **Appointment**: Represents a reserved slot. Key attributes: Client (relationship), Barber (relationship), Service (relationship), Date, Start Time, End Time (calculated as Start Time + Service Duration), Status (Scheduled, Completed, Cancelled), Active Status (Boolean).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of conflicting appointment booking requests (same barber, overlapping time interval) are blocked with a clear validation message.
- **SC-002**: Clients can complete the registration and booking flow in under 3 minutes.
- **SC-003**: 100% of logical deletion actions successfully hide the target entity from normal booking flows while preserving the record in the database for auditing.
- **SC-004**: Zero (0) unauthorized data exposure incidents (no client can view another client's booking details via direct URL navigation or API parameter tampering).
- **SC-005**: The admin dashboard updates list results in under 2 seconds when filtering by date or status.

## Assumptions

- **ASSUMPTION-001**: Barbers are managed by the administrator, and their working hours are assumed to be fixed (e.g., Monday - Saturday, 9:00 AM to 8:00 PM). There is no requirement for dynamic barber shifts in V1.
- **ASSUMPTION-002**: Appointment end times are calculated automatically based on the start time and the fixed duration of the selected service.
- **ASSUMPTION-003**: The UI will be constructed as a server-rendered web application using vanilla CSS (no Single Page Application framework).
- **ASSUMPTION-004**: Users (both staff and clients) will access the system via modern web browsers and have stable internet connectivity.
