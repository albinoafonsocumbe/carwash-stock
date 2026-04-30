from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nome', models.CharField(max_length=100)),
                ('quantidade', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('unidade', models.CharField(max_length=20)),
                ('preco', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
            options={
                'db_table': 'produtos',
                'managed': False,
            },
        ),
    ]
