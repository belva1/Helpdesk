# Generated by Django 4.2.5 on 2023-10-20 08:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0014_delete_restorationticketrequest'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='topic',
            field=models.CharField(max_length=18),
        ),
    ]