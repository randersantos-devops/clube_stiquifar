# Generated by Django 5.0 on 2024-09-20 11:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invite', '0004_alter_inviteticket_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inviteticket',
            name='dt_emissao',
            field=models.DateTimeField(default='00/00/0000'),
        ),
    ]
