# Generated by Django 5.0.6 on 2024-08-04 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0007_customuser_created_at'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='about',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='scout_organisation',
        ),
        migrations.AddField(
            model_name='customuser',
            name='about_me',
            field=models.TextField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='bund',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='stamm',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='scout_display_name',
            field=models.CharField(default='', max_length=50, unique=True),
        ),
    ]