from django.urls import path
from .api_views import (
    RegisterView, UserProfileView, ChangePasswordView,
    PasswordResetConfirmView, PasswordResetRequestView,
    EmailVerView, LogoutView, ResendVerificationEmailView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('resend-verification/', ResendVerificationEmailView.as_view(), name='resend-verification'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('profile/change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('verify-email/<uidb64>/<token>/', EmailVerView.as_view(), name='verify-email'),
    path('logout/', LogoutView.as_view(), name='logout'),
]