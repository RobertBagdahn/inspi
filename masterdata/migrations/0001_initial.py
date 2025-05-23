# Generated by Django 5.1.4 on 2025-03-05 20:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EatHabit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('public', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ZipCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('zip_code', models.CharField(blank=True, max_length=5)),
                ('city', models.CharField(blank=True, max_length=60)),
                ('lat', models.DecimalField(decimal_places=15, default=0.0, max_digits=20)),
                ('lon', models.DecimalField(decimal_places=15, default=0.0, max_digits=20)),
                ('state', models.CharField(choices=[('BW', 'Baden-Württemberg'), ('BY', 'Bayern'), ('BE', 'Berlin'), ('BB', 'Brandenburg'), ('HB', 'Bremen'), ('HH', 'Hamburg'), ('HE', 'Hessen'), ('MV', 'Mecklenburg-Vorpommern'), ('NI', 'Niedersachsen'), ('NW', 'Nordrhein-Westfalen'), ('RP', 'Rheinland-Pfalz'), ('SL', 'Saarland'), ('SN', 'Sachsen'), ('ST', 'Sachsen-Anhalt'), ('SH', 'Schleswig-Holstein'), ('TH', 'Thüringen')], default='BY', max_length=2)),
                ('created_at', models.DateTimeField(auto_now=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ScoutHierarchy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=60)),
                ('slug', models.SlugField(blank=True, max_length=60, null=True, unique=True)),
                ('abbreviation', models.CharField(blank=True, max_length=5, null=True)),
                ('full_name', models.CharField(blank=True, max_length=200, null=True)),
                ('description', models.CharField(blank=True, max_length=1000)),
                ('level_choice', models.CharField(choices=[('Verband', 'Verband'), ('Bund', 'Bund'), ('Ring', 'Regional'), ('Stamm', 'Stamm'), ('Gruppe', 'Gruppe')], default='Gruppe', max_length=10)),
                ('created_at', models.DateTimeField(auto_now=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('exist_from', models.DateField(blank=True, default='1970-01-01', null=True)),
                ('exist_till', models.DateField(blank=True, null=True)),
                ('status', models.CharField(blank=True, max_length=60, null=True)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='scouthierarchy', to='masterdata.scouthierarchy')),
                ('zip_code', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='masterdata.zipcode')),
            ],
        ),
    ]
