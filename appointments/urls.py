from django.urls import path
from django.shortcuts import redirect
from . import views
from django.contrib.auth import views as auth_views
def root_redirect(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        return redirect('dashboard')
    return redirect('login')

urlpatterns = [
    # Root redirect URL
    path('', root_redirect, name='root'),

    # Authentication URLs
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Client Portal URLs
    path('dashboard/', views.client_dashboard, name='dashboard'),
    path('book/', views.client_book_appointment, name='book'),
    path('appointments/<int:id>/cancel/', views.client_cancel_appointment, name='cancel_appointment'),

    # Administrative Portal URLs
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/appointments/book/', views.admin_book_appointment, name='admin_book'),

    # Recuperación de contraseña
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        email_template_name='registration/password_reset_email.html',
        success_url='/password-reset/done/'
    ), name='password_reset'),

    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),

    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html',
        success_url='/password-reset-complete/'
    ), name='password_reset_confirm'),

    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),
]
