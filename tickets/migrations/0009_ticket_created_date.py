# Generated by Django 4.2.5 on 2023-10-15 12:14

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0008_restorationticketrequest_created_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
