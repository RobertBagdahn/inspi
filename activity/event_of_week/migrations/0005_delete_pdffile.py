# Generated by Django 5.0.6 on 2024-11-15 13:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('event_of_week', '0004_alter_pdffile_color'),
    ]

    operations = [
        migrations.DeleteModel(
            name='PdfFile',
        ),
    ]