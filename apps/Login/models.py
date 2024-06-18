from django.contrib.auth.models import AbstractUser
from django.db import models

from main.settings import MEDIA_URL, STATIC_URL


class User(AbstractUser):
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, default='users/default.jpg')
    # Agrega otros campos según sea necesario
