# Generated by Django 5.1.3 on 2024-11-17 17:42

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activity', '0005_alter_comment_is_approved'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='costs_rating',
            field=models.CharField(choices=[('0', '0 €'), ('1', '0,50 €'), ('2', '1,00 €'), ('3', '2,00 €'), ('4', 'mehr als 2,00 €')], default='0', max_length=20),
        ),
        migrations.AlterField(
            model_name='activity',
            name='difficulty',
            field=models.CharField(choices=[('0', 'Einfach'), ('1', 'Mittel'), ('2', 'Schwer')], default='0', max_length=20),
        ),
        migrations.AlterField(
            model_name='activity',
            name='execution_time',
            field=models.CharField(choices=[('0', '<30 min'), ('1', '30 min'), ('2', '60 min'), ('3', '90 min'), ('4', 'mehr als 90 min')], default='0', max_length=20),
        ),
        migrations.AlterField(
            model_name='activity',
            name='preparation_time',
            field=models.CharField(choices=[('0', 'keine'), ('1', '5 min'), ('2', '30 min'), ('3', '60 min'), ('4', 'mehr als 60 min')], default='0', max_length=20),
        ),
        migrations.AlterField(
            model_name='activity',
            name='summary_long',
            field=models.CharField(blank=True, default='', max_length=1000, validators=[django.core.validators.MaxLengthValidator(1000)]),
        ),
    ]