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
        # Verifica perfil elevado temporariamente via sessao
        if hasattr(self, '_perfil_elevado'):
            return self._perfil_elevado == 'admin'
        return self.perfil == 'admin'

    def get_perfil_display_atual(self):
        """Retorna o perfil actual incluindo elevacao temporaria."""
        if hasattr(self, '_perfil_elevado') and self._perfil_elevado == 'admin':
            return 'Admin'
        return self.get_perfil_display()

    def __str__(self):
        return f"{self.email} ({self.get_perfil_display()})"
