from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from django.core.validators import EmailValidator
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'avatar', 'date_joined', 'last_login']
        read_only_fields = ['email', 'date_joined', 'last_login']
        
class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[EmailValidator(message=_("Enter a valid email address."))]
    )
    name = serializers.CharField(
        required=True,
        min_length=2,
        max_length=30,
        error_messages={
            'required': _('Please provide your name.'),
            'blank': _('Name cannot be empty.'),
            'min_length': _('Name must be at least 2 characters long.'),
            'max_length': _('Name cannot be longer than 30 characters.')
        }
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        min_length=8,
        error_messages={
            'min_length': _('Password must be at least 8 characters long.')
        }
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True
    )
    
    class Meta:
        model = User
        fields = ('email', 'name', 'password', 'password2')
        
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(_("A user with this email already exists."))
        return value
        
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": _("Passwords don't match.")})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(
        validators=[EmailValidator(message=_("Enter a valid email address."))]
    )
    
    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(_("No user is associated with this email address."))
        return value

class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password],
        min_length=8,
        error_messages={
            'min_length': _('Password must be at least 8 characters long.')
        }
    )
    new_password2 = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError(
                {"new_password": _("Password fields didn't match.")}
            )
        return attrs
    
class EmailVerSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True, 
        validators=[validate_password],
        min_length=8,
        error_messages={
            'min_length': _('Password must be at least 8 characters long.')
        }
    )
    new_password2 = serializers.CharField(required=True)
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(_("Old password is incorrect."))
        return value
    
    def validate(self, attrs):
        if attrs['new_password'] == attrs['old_password']:
            raise serializers.ValidationError(
                {"new_password": _("New password must be different from old password.")}
            )
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError(
                {"new_password2": _("The two password fields didn't match.")}
            )
        return attrs
    
class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField(required=False)
    
class ResendVerificationEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(
        validators=[EmailValidator(message=_("Enter a valid email address."))]
    )
    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(_("No user with this email exists."))
        return value