from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nome', models.CharField(max_length=100)),
                ('descricao', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'servicos',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ServiceProduct',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('servico', models.ForeignKey(
                    db_column='servico_id',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='produtos',
                    to='services.service',
                )),
                ('produto', models.ForeignKey(
                    db_column='produto_id',
                    on_delete=django.db.models.deletion.CASCADE,
                    to='products.product',
                )),
                ('quantidade_usada', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
            options={
                'db_table': 'consumo_servico',
                'managed': False,
            },
        ),
    ]
