# Generated by Django 5.1.4 on 2025-02-08 21:27

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0014_inspigroupnews'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inspigroupnews',
            name='message',
            field=ckeditor.fields.RichTextField(),
        ),
    ]
