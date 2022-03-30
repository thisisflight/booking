# Generated by Django 4.0.2 on 2022-03-27 21:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hotels', '0002_reservation_hotel'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='review',
            name='hotel',
        ),
        migrations.RemoveField(
            model_name='review',
            name='user',
        ),
        migrations.AddField(
            model_name='review',
            name='reservation',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='hotels.reservation', verbose_name='Бронь'),
        ),
    ]