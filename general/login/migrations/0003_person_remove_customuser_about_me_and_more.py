# Generated by Django 5.1.4 on 2024-12-30 18:51

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0002_customuser_mobile'),
    ]

    operations = [
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.UUIDField(auto_created=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('scout_name', models.CharField(blank=True, max_length=100, null=True)),
                ('first_name', models.CharField(default='', max_length=100)),
                ('last_name', models.CharField(default='', max_length=100)),
                ('address', models.CharField(blank=True, max_length=200, null=True)),
                ('address_supplement', models.CharField(blank=True, max_length=100, null=True)),
                ('zip_code', models.CharField(blank=True, max_length=5, null=True)),
                ('city', models.CharField(blank=True, max_length=100, null=True)),
                ('gender', models.CharField(choices=[('M', 'Männlich'), ('F', 'Weiblich'), ('O', 'Divers'), ('N', 'Nicht angegeben')], default='N', max_length=1)),
                ('birthday', models.DateField(blank=True, null=True)),
                ('eat_habits', models.CharField(choices=[('V', 'Vegetarisch'), ('VEG', 'Vegan'), ('A', 'Alles')], default='A', max_length=10)),
                ('about_me', models.TextField(blank=True, max_length=500, null=True)),
                ('stamm', models.CharField(blank=True, max_length=50, null=True)),
                ('bund', models.CharField(blank=True, max_length=50, null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='about_me',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='bund',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='stamm',
        ),
        migrations.AddField(
            model_name='customuser',
            name='person',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='login.person'),
        ),
    ]