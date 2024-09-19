# Generated by Django 5.0 on 2024-09-05 14:31

import datetime
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monthly_payment', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='name_payment',
            field=models.CharField(default=django.utils.timezone.now, max_length=255, verbose_name='Nome do pagador'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ticket',
            name='payment_method',
            field=models.CharField(choices=[('CARTAO DE CREDITO', 'CARTAO DE CREDITO'), ('CARTAO DE DEBITO', 'CARTAO DE DEBITO'), ('DINHEIRO', 'DINHEIRO'), ('PIX', 'PIX')], default=datetime.datetime(2024, 9, 5, 14, 31, 54, 19680), max_length=30, verbose_name='Forma de Pagamento'),
            preserve_default=False,
        ),
    ]
