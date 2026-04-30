from django.db import models


class TipoLavagem(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    duracao_minutos = models.IntegerField(default=30)
    is_active = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'tipos_lavagem'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Lavagem(models.Model):
    matricula = models.CharField(max_length=20)
    tipo_lavagem = models.ForeignKey(
        TipoLavagem, on_delete=models.PROTECT,
        db_column='tipo_lavagem_id', null=True, blank=True
    )
    data = models.DateTimeField(auto_now_add=True)
    observacoes = models.TextField(blank=True, null=True)
    funcionario = models.CharField(max_length=100, blank=True, null=True)
    valor_cobrado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    foto = models.ImageField(upload_to='lavagens/', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lavagens'
        ordering = ['-data']

    def __str__(self):
        return f"{self.matricula} — {self.tipo_lavagem}"
