from django.db import models


class Service(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tempo_estimado = models.PositiveIntegerField(default=30, help_text='Tempo em minutos')
    foto = models.ImageField(upload_to='servicos/', blank=True, null=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'servicos'
        verbose_name = 'Serviço'
        verbose_name_plural = 'Serviços'
        ordering = ['nome']

    def __str__(self):
        return self.nome

    @property
    def tempo_display(self):
        if self.tempo_estimado >= 60:
            h = self.tempo_estimado // 60
            m = self.tempo_estimado % 60
            return f'{h}h{m:02d}m' if m else f'{h}h'
        return f'{self.tempo_estimado} min'


class ServiceProduct(models.Model):
    servico = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='produtos',
        db_column='servico_id',
    )
    produto = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        db_column='produto_id',
    )
    quantidade_usada = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'consumo_servico'
        verbose_name = 'Consumo de Serviço'
        verbose_name_plural = 'Consumos de Serviço'

    def __str__(self):
        return f"{self.servico} - {self.produto} ({self.quantidade_usada})"
