# Tasks: Appointment Booking System

**Input**: Design documents from `/specs/001-appointment-booking/`

**Prerequisites**: [plan.md](file:///D:/barbertime-proyectoFinal/specs/001-appointment-booking/plan.md) (required), [spec.md](file:///D:/barbertime-proyectoFinal/specs/001-appointment-booking/spec.md) (required for user stories), [research.md](file:///D:/barbertime-proyectoFinal/specs/001-appointment-booking/research.md), [data-model.md](file:///D:/barbertime-proyectoFinal/specs/001-appointment-booking/data-model.md), [web-endpoints.md](file:///D:/barbertime-proyectoFinal/specs/001-appointment-booking/contracts/web-endpoints.md)

**Tests**: Tests are MANDATORY for every user story as per the project constitution. Write them first (Test-First methodology).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure.

- [X] T001 Initialize project dependencies configuration in `requirements.txt`
- [X] T002 Initialize Django project in `barbertime/` and create the app `appointments/` in the repository root
- [X] T003 [P] Configure environment variable reading and database parsing in `barbertime/settings.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T004 Define the base `SoftDeleteModel` class and custom manager in `appointments/models.py`
- [X] T005 [P] Configure static files serving via WhiteNoise and root URL routing in `barbertime/settings.py` and `barbertime/urls.py`
- [X] T006 Create the shared base HTML skeleton structure in `appointments/templates/base.html`
- [X] T007 [P] Implement base visual design CSS stylesheet in `appointments/static/css/style.css`
- [X] T008 Run initial database migrations using `manage.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel.

---

## Phase 3: User Story 1 - Client Registration & Authentication (Priority: P1) 🎯 MVP

**Goal**: Allow visitor self-registration (name, phone, password) and secure session-based login.

**Independent Test**: Register a new client, verify login state, and log out.

### Tests for User Story 1 (MANDATORY) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T009 [P] [US1] Write registration and login form/view tests in `appointments/tests/test_views.py`

### Implementation for User Story 1

- [X] T010 [P] [US1] Create the `Cliente` model with OneToOne link to `User` in `appointments/models.py`
- [X] T011 [US1] Create client registration form validation logic in `appointments/forms.py`
- [X] T012 [US1] Implement views for client registration, login, and logout in `appointments/views.py`
- [X] T013 [P] [US1] Design HTML template for registration form in `appointments/templates/registration/register.html`
- [X] T014 [P] [US1] Design HTML template for login form in `appointments/templates/registration/login.html`
- [X] T015 [US1] Configure authentication routing in `appointments/urls.py`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently.

---

## Phase 4: User Story 2 - Client Booking & Appointment Management (Priority: P1)

**Goal**: Allow authenticated clients to view their own bookings, create a new booking, and soft-cancel them.

**Independent Test**: Log in as a client, book an appointment, view it on the dashboard, and cancel it.

### Tests for User Story 2 (MANDATORY) ⚠️

- [X] T016 [P] [US2] Write tests for client dashboard access and booking views in `appointments/tests/test_views.py`

### Implementation for User Story 2

- [X] T017 [P] [US2] Create the `Service` model with soft delete functionality in `appointments/models.py`
- [X] T018 [US2] Create the `Appointment` model and run migrations in `appointments/models.py`
- [X] T019 [US2] Implement client dashboard view filtering only owned appointments in `appointments/views.py`
- [X] T020 [US2] Implement booking form and cancellation views in `appointments/views.py`
- [X] T021 [P] [US2] Design HTML template for client dashboard in `appointments/templates/client/dashboard.html`
- [X] T022 [P] [US2] Design HTML template for booking appointment form in `appointments/templates/client/book.html`
- [X] T023 [US2] Register routing for client dashboard, booking, and cancellation in `appointments/urls.py`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently.

---

## Phase 5: User Story 3 - Automatic Schedule Conflict Prevention (Priority: P1)

**Goal**: Prevent double-booking a barber by validating overlaps using model validation and transactional locks.

**Independent Test**: Run concurrent booking tests or overlapping requests and confirm one is blocked.

### Tests for User Story 3 (MANDATORY) ⚠️

- [X] T024 [P] [US3] Write validation and race condition tests for overlapping appointments in `appointments/tests/test_models.py`

### Implementation for User Story 3

- [X] T025 [US3] Implement overlap validation logic in the `clean()` method of `Appointment` in `appointments/models.py`
- [X] T026 [US3] Implement transactional locking (`select_for_update`) during appointment creation inside `appointments/views.py`

**Checkpoint**: Overlap validation is active. Double bookings are blocked from both client and admin channels.

---

## Phase 6: User Story 4 - Admin Management of Clients, Services, and Appointments (Priority: P2)

**Goal**: Let staff users log in and manage (create/edit/soft-delete) clients, services, and appointments of any person.

**Independent Test**: Log in as staff, add a service, deactivate a client, and book an appointment on behalf of a client.

### Tests for User Story 4 (MANDATORY) ⚠️

- [X] T027 [P] [US4] Write unit tests for staff authorization and CRUD operations in `appointments/tests/test_views.py`

### Implementation for User Story 4

- [X] T028 [US4] Implement staff-only admin view permissions and logic for managing clients and services in `appointments/views.py`
- [X] T029 [US4] Implement "Book on Behalf" of client view in `appointments/views.py`
- [X] T030 [P] [US4] Design HTML template for the staff booking form in `appointments/templates/admin/book_appointment.html`
- [X] T031 [US4] Register URL routes for admin management endpoints in `appointments/urls.py`

**Checkpoint**: Staff management features are active. Admin can manage clients, services, and bookings.

---

## Phase 7: User Story 5 - Admin Appointment Dashboard and Filtering (Priority: P2)

**Goal**: Render a master list of all appointments for staff with filtering by date and status.

**Independent Test**: Open the admin dashboard, filter by specific date and "Cancelled" status, and check results.

### Tests for User Story 5 (MANDATORY) ⚠️

- [X] T032 [P] [US5] Write tests for appointment listing and filtering query logic in `appointments/tests/test_views.py`

### Implementation for User Story 5

- [X] T033 [US5] Implement the admin dashboard appointment query list with date and status filters in `appointments/views.py`
- [X] T034 [P] [US5] Design HTML template for the admin dashboard in `appointments/templates/admin/dashboard.html`
- [X] T035 [US5] Register routing for the admin dashboard in `appointments/urls.py`

**Checkpoint**: All user stories are complete and integrated.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories.

- [X] T036 [P] Implement cascading cancellation logic for appointments when a client profile is soft-deleted in `appointments/models.py`
- [X] T037 [P] Add premium styling and micro-animations to the forms and dashboards in `appointments/static/css/style.css`
- [X] T038 Verify static files collection and Whitenoise setup using `manage.py`
- [X] T039 Execute validation checklist in `specs/001-appointment-booking/quickstart.md`
- [X] T040 Run all automated tests using `manage.py`

### Post-Implementación & Ajustes Manuales

- [X] T041 [US1] Add mandatory unique email field to `Cliente` model and registration flow in `appointments/models.py` and `appointments/forms.py`
- [X] T042 [US1] Enforce Peruvian phone number validation (9 digits starting with 9) in `appointments/forms.py`
- [X] T043 [US6] Implement password recovery flow ("Olvidé mi contraseña") using Django native `PasswordResetView` views in `appointments/urls.py` and `appointments/templates/registration/`
- [X] T044 [US1] Implement dual login support allowing clients to authenticate using either phone number or email address in `appointments/forms.py` and `appointments/views.py`
- [X] T045 [P] [US6] Implement responsive floating WhatsApp contact button in `appointments/templates/base.html` and `appointments/static/css/style.css`
- [X] T046 [P] [US6] Implement full responsive design layout (mobile, tablet, desktop) with hamburger menu, responsive tables, and fluid forms in `appointments/static/css/style.css`
- [X] T047 [P] Configure cloud deployment on Render with `render.yaml` blueprint and `build.sh` script in project root
- [X] T048 Configure project timezone to `America/Lima` (Peru) in `barbertime/settings.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories.
- **User Stories (Phase 3+)**: All depend on Foundational phase completion.
  - User Story 1 (US1) is the base authentication and client link.
  - User Story 2 (US2) depends on US1.
  - User Story 3 (US3) integrates with US2 booking.
  - User Story 4 (US4) depends on US3 validation.
  - User Story 5 (US5) depends on US4.
- **Polish (Phase 8)**: Depends on all user stories being complete.

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel.
- All Foundational tasks marked [P] can run in parallel (within Phase 2).
- Once Foundational phase completes, developers can implement US1 and US2 models and tests in parallel.
- All tests for a user story marked [P] can run in parallel.
- Templates and HTML forms can be drafted in parallel with models/views.

---

## Parallel Example: User Story 1

```bash
# Launch test creation and model creation in parallel:
Task: "Write registration and login form/view tests in appointments/tests/test_views.py"
Task: "Create the Cliente model with OneToOne link to User in appointments/models.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories).
3. Complete Phase 3: User Story 1 (Auth).
4. Complete Phase 4: User Story 2 (Booking).
5. **STOP and VALIDATE**: Test client registration and simple booking flow.

### Incremental Delivery

1. Complete Setup + Foundational.
2. Add US1 (Client Registration/Login) -> Test -> MVP Gate 1.
3. Add US2 (Client booking/cancellation) -> Test -> MVP Gate 2.
4. Add US3 (Conflict Validation) -> Run concurrent tests.
5. Add US4 (Admin Management) -> Test admin capability.
6. Add US5 (Admin filtering) -> Run E2E scenarios.
7. Perform Polish & Final Audit.

---

## Notes

- [P] tasks = different files, no dependencies.
- [Story] label maps task to specific user story for traceability.
- Each user story is independently completable and testable.
- Verify tests fail before implementing (Test-First methodology).
