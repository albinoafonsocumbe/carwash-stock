from django.db import models
from django.conf import settings


class StockMovement(models.Model):
    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('saida', 'Saída'),
    ]

    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    quantidade = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateTimeField(auto_now_add=True)
    produto = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        db_column='produto_id',
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        null=True, blank=True, db_column='owner_id'
    )

    class Meta:
        managed = False
        db_table = 'movimentos'
        verbose_name = 'Movimentação de Stock'
        verbose_name_plural = 'Movimentações de Stock'
        ordering = ['-data']

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.produto} ({self.quantidade})"
