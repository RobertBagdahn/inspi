# Generated by Django 5.1.3 on 2024-12-15 09:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0003_mealitem_meta_info'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mealeventtemplate',
            old_name='animal_products',
            new_name='animal_product',
        ),
        migrations.RemoveField(
            model_name='ingredient',
            name='animal_products',
        ),
    ]