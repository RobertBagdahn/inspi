# Generated by Django 5.1.4 on 2024-12-24 09:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0009_remove_inspigrouppermission_subgroup_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='inspigroup',
            old_name='date_cancelled',
            new_name='date_deleted',
        ),
        migrations.RenameField(
            model_name='inspigroup',
            old_name='cancel_requested_by',
            new_name='delete_requested_by',
        ),
        migrations.RenameField(
            model_name='inspigroup',
            old_name='is_cancelled',
            new_name='is_deleted',
        ),
        migrations.AlterField(
            model_name='inspigrouppermission',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='permissions', to='group.inspigroup'),
        ),
        migrations.AlterField(
            model_name='inspigrouppermission',
            name='parent_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subgroup_permissions', to='group.inspigroup'),
        ),
        migrations.DeleteModel(
            name='InspiGroupInvitation',
        ),
    ]