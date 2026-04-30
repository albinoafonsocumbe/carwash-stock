from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    PERFIL_CHOICES = [
        ('admin', 'Admin'),
        ('funcionario', 'Funcionario'),
    ]
    perfil = models.CharField(
        max_length=20,
        choices=PERFIL_CHOICES,
        default='funcionario',
        verbose_name='Perfil',
    )
    email = models.EmailField(unique=True, verbose_name='Email')

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = 'Utilizador'
        verbose_name_plural = 'Utilizadores'

    def is_admin(self):
        return self.perfil == 'admin'

    def __str__(self):
        return f"{self.email} ({self.get_perfil_display()})"
