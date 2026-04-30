from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='StockMovement',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('tipo', models.CharField(max_length=10)),
                ('quantidade', models.DecimalField(decimal_places=2, max_digits=10)),
                ('data', models.DateTimeField(auto_now_add=True)),
                ('produto', models.ForeignKey(
                    db_column='produto_id',
                    on_delete=django.db.models.deletion.CASCADE,
                    to='products.product',
                )),
            ],
            options={
                'db_table': 'movimentos',
                'managed': False,
            },
        ),
    ]
