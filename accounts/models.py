from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=11, unique=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
