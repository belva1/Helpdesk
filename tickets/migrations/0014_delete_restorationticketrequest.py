# Generated by Django 4.2.5 on 2023-10-19 16:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0013_remove_ticket_reject_reason'),
    ]

    operations = [
        migrations.DeleteModel(
            name='RestorationTicketRequest',
        ),
    ]