from django.contrib.auth.models import AbstractUser
from django.db import models

from main.settings import MEDIA_URL, STATIC_URL


class User(AbstractUser):
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, default='users/default.jpg')

    def __str__(self):
        # Se presenta el primer nombre y primer apellido y no los dos.
        return '{} {}'.format(self.first_name.split(' ')[0], self.last_name.split(' ')[0])

    def save(self, *args, **kwargs):
        try:
            # Obtenemos la imagen actual para eleminarla y luego guardamos la nueva
            this = User.objects.get(id=self.id)
            if this.profile_picture != self.profile_picture and this.profile_picture != 'users/default.jpg':
                this.profile_picture.delete(save=False)
        except User.DoesNotExist:
            pass
        super(User, self).save(*args, **kwargs)
