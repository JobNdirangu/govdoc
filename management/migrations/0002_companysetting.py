# Generated by Django 5.0.7 on 2024-11-22 22:22

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanySetting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(default='W&SMS', max_length=100)),
                ('discount_percentage', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('theme_choice', models.CharField(choices=[('default', 'Default'), ('dark', 'Dark'), ('light', 'Light'), ('green', 'Green')], default='default', max_length=20)),
                ('min_points_to_redeem', models.PositiveIntegerField(default=0)),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='company_settings', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
