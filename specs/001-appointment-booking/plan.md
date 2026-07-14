# Implementation Plan: Appointment Booking System

**Branch**: `001-appointment-booking` | **Date**: 2026-07-14 | **Spec**: [spec.md](file:///D:/barbertime-proyectoFinal/specs/001-appointment-booking/spec.md)

**Input**: Feature specification from `/specs/001-appointment-booking/spec.md`

## Summary

The objective is to implement a web-based appointment booking system for the BarberTime barber shop. The application will be built using Python 3.11+, Django 5 (MVT pattern), and PostgreSQL. The UI will be server-rendered with Django templates and styled using vanilla CSS. Clients will be able to self-register, login, book appointments without conflicts, and view/cancel their bookings. Administrative staff will manage clients, services, and all appointments with search/filter capabilities.

---

## Technical Context

- **Language/Version**: Python 3.11+
- **Primary Dependencies**: Django 5, dj-database-url, gunicorn, whitenoise, psycopg2-binary (No SPA/React/Vue frontend frameworks)
- **Storage**: PostgreSQL (hosted on Render in production, local for development)
- **Testing**: Django integrated unit and integration testing framework (django.test)
- **Target Platform**: Render Cloud (Web Service for App, Managed PostgreSQL for DB)
- **Project Type**: Server-Rendered Web Application (MVT)
- **Performance Goals**: All dashboard pages render and load in under 2 seconds.
- **Constraints**: 
  - Session-based authentication via `django.contrib.auth`.
  - Strict data isolation: clients must not access other clients' appointments.
  - Automatic double-booking validation with transaction locks to prevent concurrency race conditions.
  - Logical deletion (soft delete) applied to all core entities (Client, Service, Appointment).

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Gate I: Specification-First**: Passed. The specification `spec.md` has been written and validated prior to creating the implementation plan.
- **Gate II: Stack Constraints (Django + Postgres + server rendering)**: Passed. Strict adherence to Python 3.11+, Django MVT, and PostgreSQL. No React/Vue/SPA frontend frameworks.
- **Gate III: Test-First**: Passed. Automated tests will be written prior to code implementation.
- **Gate IV: Simplicidad (YAGNI)**: Passed. The scope is limited strictly to user accounts, booking, deactivation, and filtering.
- **Gate V: Borrado Lógico**: Passed. Soft delete is designed into the core models.
- **Gate VI: Roles y Privacidad**: Passed. Separate admin vs client access controls and database-level isolation checks.
- **Gate VII: Gestión con Scrum**: Passed. The work is chunked into logical units.

---

## Project Structure

The project will follow a standard single-project Django layout:

```text
specs/001-appointment-booking/
├── plan.md              # This file
├── research.md          # Research decisions
├── data-model.md        # DB tables and models
├── quickstart.md        # Run and verification guide
└── contracts/
    └── web-endpoints.md # Route and interface contract

barbertime/              # Django Project Root Config
├── __init__.py
├── settings.py          # App settings (PostgreSQL parsing, WhiteNoise, static files)
├── urls.py              # Root router mapping to appointments app
├── wsgi.py              # Gunicorn deployment config
└── asgi.py

appointments/            # Core App Module
├── migrations/          # DB migration files
├── templates/           # HTML Templates
│   ├── base.html        # Shared base shell
│   ├── registration/    # Login and registration templates
│   ├── client/          # Customer dashboard and booking views
│   └── admin/           # Administrative portal templates
├── static/              # Assets
│   └── css/             # Vanilla CSS sheets
│   │   └── style.css    # Stylesheet enforcing premium visual design
├── __init__.py
├── admin.py             # Django admin configuration
├── apps.py
├── forms.py             # Form definitions (auth, booking validation)
├── models.py            # DB schemas with SoftDelete base model
├── tests/               # Test suites (written test-first)
│   ├── __init__.py
│   ├── test_models.py   # Model and overlap validation tests
│   └── test_views.py    # Route security and user journey tests
├── urls.py              # App routing
└── views.py             # Server MVT views and business logic

manage.py
requirements.txt
```

**Structure Decision**: Single-project Django application layout. All functionality is encapsulated within a single Django app (`appointments`) alongside the project config (`barbertime`), maintaining simplicity and avoiding overengineering.

---

## Complexity Tracking

*No violations of the Constitution were identified. Standard structures are strictly followed.*
