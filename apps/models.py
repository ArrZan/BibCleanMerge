from django.db import models
from django.contrib.auth.models import User


# class UserModel(User):
#     nombre = models.CharField(max_length=50, null=True)
#     apellidoPat = models.CharField("Apellido paterno", max_length=50, null=True)
#     apellidoMat = models.CharField("Apellido materno", max_length=50, null=True)
#     cedula = models.CharField(max_length=10, null=True)
#     photo = models.FileField(upload_to='estudiantes/fotos/', blank=True, null=True)
#
#     def __str__(self):
#         return '{} - {}'.format(self.cedula, self.apellidoPat)
#
#     class Meta:
#         verbose_name = "Estudiante"
#         verbose_name_plural = "Estudiantes"
#         ordering = ('apellidoPat',)
#
#     def get_image(self):
#         if self.foto:
#             return '{}{}'.format(settings.MEDIA_URL, self.foto)
#
#         return '{}{}'.format(settings.STATIC_URL, settings.PHOTO_USER_EMPTY)
