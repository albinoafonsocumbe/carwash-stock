from django.db import models


class Product(models.Model):
    nome = models.CharField(max_length=100)
    quantidade = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unidade = models.CharField(max_length=20)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    nivel_minimo = models.DecimalField(max_digits=10, decimal_places=2, default=5)

    class Meta:
        managed = False
        db_table = 'produtos'
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['nome']

    @property
    def tem_alerta(self):
        return self.quantidade <= self.nivel_minimo

    def __str__(self):
        return self.nome
