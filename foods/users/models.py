from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
# Create your models here.

class AppUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Please Enter An Email")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_user(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)
    
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff= true")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("superuser must have is_superuser= true")
        return self._create_user(email, password, **extra_fields)
    
class User(AbstractUser):
    username = None
    email = models.EmailField(_("email adress"), unique=True)
    name = models.CharField(max_length=30)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    
    objects = AppUserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]
    
    def __str__(self):
        return self.name