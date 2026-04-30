from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name='TipoLavagem',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nome', models.CharField(max_length=100)),
                ('descricao', models.TextField(blank=True, null=True)),
                ('preco', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('duracao_minutos', models.IntegerField(default=30)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={'db_table': 'tipos_lavagem', 'managed': False},
        ),
        migrations.CreateModel(
            name='Lavagem',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('matricula', models.CharField(max_length=20)),
                ('data', models.DateTimeField(auto_now_add=True)),
                ('observacoes', models.TextField(blank=True, null=True)),
                ('funcionario', models.CharField(blank=True, max_length=100, null=True)),
                ('valor_cobrado', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('tipo_lavagem', models.ForeignKey(
                    db_column='tipo_lavagem_id', null=True, blank=True,
                    on_delete=django.db.models.deletion.PROTECT,
                    to='lavagens.tipolavagem',
                )),
            ],
            options={'db_table': 'lavagens', 'managed': False},
        ),
    ]
