# Research: Appointment Booking System

This document outlines the technical research, architectural decisions, and best practices for implementing the BarberTime appointment booking system using Django and PostgreSQL deployed on Render.

---

## Technical Decisions

### 1. Database URL Parsing & Configuration
- **Decision**: Use the `dj-database-url` package in `settings.py` to parse the `DATABASE_URL` environment variable.
- **Rationale**: Storing database configuration in a single connection string (`DATABASE_URL`) is a 12-factor app standard. Render provides this variable automatically for managed databases, making configuration seamless between local development and production.
- **Alternatives Considered**: 
  - Manually parsing connection parameters from `DATABASE_URL` (rejected as complex and error-prone).
  - Hardcoding connection dictionaries (rejected as it violates security and configuration separation).

### 2. Logical Deletion (Soft Delete)
- **Decision**: Implement a custom abstract base model `SoftDeleteModel` with an `is_active` boolean field, overriding the standard `delete()` method to set `is_active = False` and save, and a custom Manager (`ActiveManager`) to filter out inactive objects by default.
- **Rationale**: Required by Constitution Principle V. Creating a reusable abstract model keeps the codebase DRY (Don't Repeat Yourself) and prevents developers from forgetting to apply soft delete filters.
- **Alternatives Considered**:
  - Manual logical delete filtering in every view (rejected as highly error-prone and hard to maintain).
  - Third-party packages like `django-safedelete` (rejected to maintain simplicity and avoid external dependencies).

### 3. Concurrency & Overlap Validation (Double-Booking Prevention)
- **Decision**: 
  1. Validate overlapping intervals in the model's `clean()` method by searching for existing active appointments for the same barber where:
     `start_time < existing_end_time` AND `end_time > existing_start_time`.
  2. Implement database-level serialization by wrapping the booking view in a Django database transaction (`transaction.atomic`) and using `select_for_update()` to lock the barber record during slot checking and booking.
- **Rationale**: The combination of model-level validation (for user feedback) and database transaction locks (for concurrency safety) prevents race conditions where two clients book the same barber for overlapping slots at the same millisecond.
- **Alternatives Considered**:
  - Application-level lock in Redis or memory (rejected as it adds infrastructure complexity).
  - Checking availability only at the front-end level (rejected as insecure and easily bypassed).

### 4. Client Authentication and Roles
- **Decision**: Use Django's built-in session-based authentication (`django.contrib.auth`) and a standard `django.contrib.auth.models.User` model. The client's phone number will act as the `username`. A separate `Cliente` model will maintain a `OneToOneField` link to the `User` model to store additional client-specific data.
- **Rationale**: Simple, highly secure, and utilizes Django's mature session management out of the box, adhering strictly to the authentication constraints. Using the phone number as the username ensures logins are unique without requiring a complex custom User subclass.
- **Alternatives Considered**:
  - Custom User model subclassing `AbstractBaseUser` (rejected as it introduces migration complications and configuration overhead for simple phone-based login).

### 5. Static Files Management on Render
- **Decision**: Use `whitenoise` to serve static files (CSS, JS) directly from the Django application server.
- **Rationale**: Render does not have a built-in persistent static files host for free web services. WhiteNoise allows Django to serve its own static files efficiently without needing a CDN or complex external services.
- **Alternatives Considered**:
  - Serving static files via Django's default development server view in production (disabled by Django for security/performance reasons).
  - AWS S3 bucket (rejected as it exceeds the "no external infrastructure" constraint).

---

## Best Practices

### Django + PostgreSQL on Render
- **Prerequisites**: Always install `gunicorn` as the production application server and `psycopg2-binary` (or `psycopg[c]` for Django 5) for PostgreSQL connectivity.
- **Security**:
  - `DEBUG` must be set to `False` in production using environment variables.
  - `SECRET_KEY` must be loaded from an environment variable.
  - Allowed hosts must be configured to include the Render service domain (e.g., `['.onrender.com']`).
- **Database Migrations**: Run migrations during the Render build/deploy phase using a start script or the custom "Build Command" configuration (`python manage.py migrate`).
