# Generated by Django 5.0.6 on 2024-11-13 22:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event_of_week', '0002_pdffile_delete_book'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pdffile',
            name='color',
            field=models.CharField(choices=[(1, 'Rot'), (2, 'Blau'), (3, 'Orange')], default=1, max_length=100),
        ),
    ]