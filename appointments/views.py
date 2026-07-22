from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import Cliente, Service, Appointment
from .forms import ClientRegistrationForm, ClientAppointmentForm, AdminAppointmentForm
from datetime import date, datetime

# Access control tests
def staff_member_required(view_func):
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.is_staff,
        login_url='login'
    )
    return actual_decorator(view_func)

def client_required(view_func):
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and not u.is_staff and hasattr(u, 'cliente'),
        login_url='login'
    )
    return actual_decorator(view_func)


# Authentication views
def register_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        return redirect('dashboard')

    if request.method == 'POST':
        form = ClientRegistrationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    name = form.cleaned_data['name']
                    phone = form.cleaned_data['phone']
                    password = form.cleaned_data['password']

                    email = form.cleaned_data['email']

                    # Create standard Django user
                    user = User.objects.create_user(
                        username=phone,
                        password=password,
                        first_name=name,
                        email=email
                    )
                    
                    # Create linked client profile
                    Cliente.objects.create(user=user, phone=phone, email=email)

                    # Automatically log in the client
                    login(request, user)
                    messages.success(request, "¡Registro completado con éxito! Bienvenido a BarberTime!")
                    return redirect('dashboard')
            except Exception as e:
                form.add_error(None, "Ocurrió un error al procesar el registro. Inténtelo de nuevo.")
    else:
        form = ClientRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})


# Direct Login View handling routing
# Direct Login View handling routing
def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        return redirect('dashboard')

    if request.method == 'POST':
        identificador = request.POST.get('username', '').strip()
        password = request.POST.get('password')

        # Si el usuario escribió un correo, buscamos a qué teléfono (username) corresponde
        username_real = identificador
        if '@' in identificador:
            try:
                cliente_encontrado = Cliente.objects.get(email=identificador)
                username_real = cliente_encontrado.user.username
            except Cliente.DoesNotExist:
                username_real = identificador  # dejará fallar la autenticación normalmente

        # Verify credentials
        from django.contrib.auth import authenticate
        user = authenticate(request, username=username_real, password=password)
        
        if user is not None:
            if user.is_active:
                nombre_mostrar = user.first_name or user.username
                login(request, user)
                messages.success(request, f"¡Hola de nuevo, {nombre_mostrar}!")
                if user.is_staff:
                    return redirect('admin_dashboard')
                return redirect('dashboard')
            else:
                messages.error(request, "Esta cuenta ha sido desactivada.")
        else:
            messages.error(request, "Número de teléfono/correo o contraseña incorrectos.")

    return render(request, 'registration/login.html')


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.info(request, "Has cerrado sesión correctamente.")
    return redirect('login')


# Client Portal views
@login_required
@client_required
def client_dashboard(request):
    cliente = request.user.cliente
    
    # Query appointments (only active/soft-active ones)
    appointments = Appointment.objects.filter(client=cliente).order_by('date', 'start_time')
    
    # Filter upcoming vs historical
    upcoming_appointments = appointments.filter(status='SCHEDULED', date__gte=date.today())
    
    past_appointments = appointments.exclude(
        id__in=upcoming_appointments.values_list('id', flat=True)
    )

    return render(request, 'client/dashboard.html', {
        'client': cliente,
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments
    })


@login_required
@client_required
def client_book_appointment(request):
    cliente = request.user.cliente
    
    if request.method == 'POST':
        form = ClientAppointmentForm(request.POST)
        if form.is_valid():
            try:
                # Wrap booking logic in transaction and lock selected barber to avoid race conditions
                barber_user = form.cleaned_data['barber']
                
                with transaction.atomic():
                    # Acquire row-level lock on the Barber User record
                    locked_barber = User.objects.select_for_update().get(id=barber_user.id)
                    
                    # Create appointment instance but don't save to DB yet
                    appointment = form.save(commit=False)
                    appointment.client = cliente
                    
                    # Triggers full validation (including overlap check in clean())
                    appointment.full_clean()
                    appointment.save()
                    
                    messages.success(request, f"Cita reservada con éxito para el {appointment.date} a las {appointment.start_time}.")
                    return redirect('dashboard')
            except ValidationError as ve:
                for field, errors in ve.message_dict.items():
                    for error in errors:
                        form.add_error(field if field != '__all__' else None, error)
            except Exception as e:
                form.add_error(None, f"No se pudo reservar la cita: {str(e)}")
    else:
        form = ClientAppointmentForm()

    return render(request, 'client/book.html', {
        'form': form,
        'services': Service.objects.filter(is_active=True),
        'barbers': User.objects.filter(is_staff=True, is_active=True)
    })


@login_required
@client_required
def client_cancel_appointment(request, id):
    if request.method == 'POST':
        cliente = request.user.cliente
        # Ensure client owns the appointment
        appointment = get_object_or_404(Appointment, id=id, client=cliente, status='SCHEDULED')
        
        # Soft delete cancellation
        appointment.status = 'CANCELLED'
        appointment.save()
        messages.success(request, "La cita ha sido cancelada correctamente.")
        
    return redirect('dashboard')


# Administrative Portal views
# Administrative Portal views
@login_required
@staff_member_required
def admin_dashboard(request):
    # Retrieve query parameters for filtering
    filter_date_str = request.GET.get('date', '').strip()
    filter_status = request.GET.get('status', 'ALL')
    
    # Base query for active appointments
    appointments = Appointment.objects.all().order_by('date', 'start_time')
    
    # Aplicar filtro de fecha SOLO si el usuario seleccionó una fecha específica
    if filter_date_str:
        try:
            filter_date = datetime.strptime(filter_date_str, '%Y-%m-%d').date()
            appointments = appointments.filter(date=filter_date)
        except ValueError:
            filter_date_str = ''

    # Apply status filter
    if filter_status != 'ALL':
        appointments = appointments.filter(status=filter_status)

    return render(request, 'admin/dashboard.html', {
        'appointments': appointments,
        'selected_date': filter_date_str,
        'selected_status': filter_status,
        'status_choices': Appointment.STATUS_CHOICES
    })

@login_required
@staff_member_required
def admin_book_appointment(request):
    if request.method == 'POST':
        form = AdminAppointmentForm(request.POST)
        if form.is_valid():
            try:
                barber_user = form.cleaned_data['barber']
                
                with transaction.atomic():
                    # Acquire row-level lock on the Barber User record
                    locked_barber = User.objects.select_for_update().get(id=barber_user.id)
                    
                    # Save appointment, clean triggers overlap check
                    appointment = form.save(commit=False)
                    appointment.full_clean()
                    appointment.save()
                    
                    messages.success(request, f"Cita creada con éxito para {appointment.client.user.first_name}.")
                    return redirect('admin_dashboard')
            except ValidationError as ve:
                for field, errors in ve.message_dict.items():
                    for error in errors:
                        form.add_error(field if field != '__all__' else None, error)
            except Exception as e:
                form.add_error(None, f"No se pudo guardar la cita: {str(e)}")
    else:
        form = AdminAppointmentForm()

    return render(request, 'admin/book_appointment.html', {
        'form': form,
        'clients': Cliente.objects.filter(is_active=True),
        'services': Service.objects.filter(is_active=True),
        'barbers': User.objects.filter(is_staff=True, is_active=True)
    })

@login_required
@staff_member_required
def admin_cancel_appointment(request, id):
    if request.method == 'POST':
        appointment = get_object_or_404(Appointment, id=id, status='SCHEDULED')
        appointment.status = 'CANCELLED'
        appointment.save()
        messages.success(request, f"La cita de {appointment.client.user.first_name} fue cancelada correctamente.")
        
    return redirect('admin_dashboard')

@login_required
@staff_member_required
def admin_complete_appointment(request, id):
    if request.method == 'POST':
        appointment = get_object_or_404(Appointment, id=id, status='SCHEDULED')
        appointment.status = 'COMPLETED'
        appointment.save()
        messages.success(request, f"La cita de {appointment.client.user.first_name} ha sido marcada como completada.")
        
    return redirect('admin_dashboard')