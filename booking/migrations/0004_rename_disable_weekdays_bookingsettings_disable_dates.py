# Generated by Django 4.0.1 on 2022-12-18 09:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0003_alter_booking_booking_no'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bookingsettings',
            old_name='disable_weekdays',
            new_name='disable_dates',
        ),
    ]
