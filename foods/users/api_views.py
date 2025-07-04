from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.throttling import AnonRateThrottle
from .models import User
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from django.conf import settings
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta
from .serializer import (
    UserSerializer, RegisterSerializer, ChangePasswordSerializer,
    PasswordResetConfirmSerializer, PasswordResetRequestSerializer,
    EmailVerSerializer, LogoutSerializer, ResendVerificationEmailSerializer
)
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.translation import gettext_lazy as _

class UserProfileView(RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user

@method_decorator(name='post', decorator=swagger_auto_schema(
    tags=['Register'],
    operation_summary="Register new user",
    operation_description="Creates a new user account and sends a verification email."
))
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        user.is_active = False
        user.save()

        current_site = get_current_site(request)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        
        verification_link = f"{'https' if request.is_secure() else 'http'}://{current_site.domain}/api/users/verify-email/{uid}/{token}/"

        # Send HTML email
        subject = _("Verify your email")
        message = render_to_string('email/verify_email.html', {
            'user': user,
            'verification_link': verification_link,
            'expiry_hours': settings.EMAIL_VERIFICATION_TIMEOUT_HOURS
        })
        
        send_mail(
            subject=subject,
            message="",  # Empty message as we're using html_message
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=message,
            fail_silently=False,
        )

        return Response({
            "message": _("User registered successfully. Please check your email to verify your account."),
            "user": self.get_serializer(user).data,
        }, status=status.HTTP_201_CREATED)

@method_decorator(name='post', decorator=swagger_auto_schema(
    tags=['Password-reset'],
    operation_summary="Request password reset",
    operation_description="Sends a password reset link to the provided email address."
))
class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AnonRateThrottle]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = User.objects.get(email=serializer.validated_data['email'])
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        
        current_site = get_current_site(request)
        reset_url = f"{'https' if request.is_secure() else 'http'}://{current_site.domain}/api/users/password-reset-confirm/{uid}/{token}/"

        # Send HTML email
        subject = _("Password Reset Request")
        message = render_to_string('email/password_reset_email.html', {
            'user': user,
            'reset_link': reset_url,
            'expiry_hours': settings.PASSWORD_RESET_TIMEOUT_HOURS
        })
        
        send_mail(
            subject=subject,
            message="",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=message,
            fail_silently=False,
        )
        
        return Response(
            {"message": _("Password reset email sent. Please check your inbox.")}, 
            status=status.HTTP_200_OK
        )

@method_decorator(name='post', decorator=swagger_auto_schema(
    tags=['Password-reset'],
    operation_summary="Confirm password reset",
    operation_description="Confirms the password reset and sets the new password."
))
class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, uidb64, token, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {"error": _("Invalid password reset link.")}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not default_token_generator.check_token(user, token):
            return Response(
                {"error": _("Invalid or expired token.")}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response(
            {"message": _("Password has been reset successfully.")}, 
            status=status.HTTP_200_OK
        )

@method_decorator(name='get', decorator=swagger_auto_schema(
    tags=['Register'],
    operation_summary="Verify user email",
    operation_description="Verifies the user's email address using the verification token."
))
class EmailVerView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {"error": _("Invalid verification link.")}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        if not default_token_generator.check_token(user, token):
            return Response(
                {"error": _("Invalid or expired token.")}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        if user.is_active:
            return Response(
                {"message": _("Email is already verified.")}, 
                status=status.HTTP_200_OK
            )

        user.is_active = True
        user.save()
        return Response(
            {"message": _("Email verified successfully.")}, 
            status=status.HTTP_200_OK
        )

@method_decorator(name='post', decorator=swagger_auto_schema(
    tags=['Register'],
    operation_summary="Resend verification email",
    operation_description="Resends the email verification link to the user."
))
class ResendVerificationEmailView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AnonRateThrottle]
    serializer_class = ResendVerificationEmailSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data) # <--- USE THE SERIALIZER
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email'] # <--- GET EMAIL FROM VALIDATED DATA

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # This case is already handled by the serializer's validate_email now,
            # but it's good to keep a general try-except for robustness.
            return Response(
                {"error": _("No user with this email exists.")},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user.is_active:
            return Response(
                {"message": _("Email is already verified.")},
                status=status.HTTP_200_OK
            )

        current_site = get_current_site(request)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        verification_link = f"{'https' if request.is_secure() else 'http'}://{current_site.domain}/users/verify-email/{uid}/{token}/"

        subject = _("Verify your email")
        message = render_to_string('email/verify_email.html', {
            'user': user,
            'verification_link': verification_link,
            'expiry_hours': settings.EMAIL_VERIFICATION_TIMEOUT_HOURS
        })

        send_mail(
            subject=subject,
            message="",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=message,
            fail_silently=False,
        )

        return Response(
            {"message": _("Verification email resent. Please check your inbox.")},
            status=status.HTTP_200_OK
        )

@method_decorator(name='patch', decorator=swagger_auto_schema(
    tags=['Password-Change'],
    operation_summary="Change password",
    operation_description="Allows authenticated users to change their password."
))
@method_decorator(name='put', decorator=swagger_auto_schema(
    tags=['Password-Change'],
    operation_summary="Change password"
))
class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        # Logout all sessions
        tokens = OutstandingToken.objects.filter(user=user)
        for token in tokens:
            BlacklistedToken.objects.get_or_create(token=token)
        
        return Response(
            {"message": _("Password updated successfully. Please login again.")}, 
            status=status.HTTP_200_OK
        )

@method_decorator(name='post', decorator=swagger_auto_schema(
    tags=["Logout"],
    operation_summary="Logout and blacklist refresh token",
    operation_description="Logs out the user by blacklisting the refresh token.",
    request_body=LogoutSerializer,
    responses={
        205: "Successfully logged out",
        400: "Invalid or expired refresh token"
    }
))
class LogoutView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LogoutSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            refresh_token = serializer.validated_data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            # Also blacklist the access token if available
            if 'access' in request.data:
                try:
                    access_token = request.data['access']
                    OutstandingToken.objects.filter(token=access_token).delete()
                except Exception:
                    pass
                    
            return Response(
                {"message": _("Successfully logged out.")}, 
                status=status.HTTP_205_RESET_CONTENT
            )
        except Exception as e:
            return Response(
                {"error": _("Invalid or expired refresh token.")}, 
                status=status.HTTP_400_BAD_REQUEST
            )