# Generated by Django 3.2.8 on 2021-10-29 14:03

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0003_purchase'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchase',
            name='time',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]