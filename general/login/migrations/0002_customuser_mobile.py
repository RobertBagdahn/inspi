# Generated by Django 5.1.4 on 2024-12-29 21:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='mobile',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
