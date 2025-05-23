# Generated by Django 5.1.7 on 2025-03-27 20:10

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0010_ingredient_recipe_counts'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='NutritionalTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(help_text="Name of the tag. E.g. 'Fleisch', 'Alkohol', 'Nüsse', Scharf", max_length=255)),
                ('name_opposite', models.CharField(help_text="Name of the tag for human readable output. e.g. 'Vegan', 'Vegetarisch', 'Alkoholfrei'", max_length=255)),
                ('description', models.CharField(max_length=255)),
                ('description_human', models.CharField(max_length=255)),
                ('rank', models.IntegerField(default=1)),
                ('is_dangerous', models.BooleanField(default=False, help_text='Indicates if this tag represents a potentially harmful or dangerous ingredient')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RecipeHint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('hint', models.CharField(blank=True, max_length=50)),
                ('improvement', models.CharField(blank=True, max_length=1000)),
                ('value', models.FloatField(default=1)),
                ('hint_level', models.CharField(choices=[('info', 'Info'), ('warn', 'Achtung'), ('error', 'Fehler')], default='info', max_length=10)),
                ('min_max', models.CharField(choices=[('max', 'Maximal'), ('min', 'Minimal')], default='min', max_length=10)),
                ('parameter', models.CharField(choices=[('weight_g', 'Gewicht (g)'), ('energy_kj', 'Energie (kJ)'), ('protein_g', 'Eiweiß (g)'), ('fat_g', 'Fett (g)'), ('fat_sat_g', 'Gesättigte Fettsäuren (g)'), ('sugar_g', 'Zucker (g)'), ('sodium_mg', 'Natrium (mg)'), ('salt_g', 'Salz (g)'), ('carbohydrate_g', 'Kohlenhydrate (g)'), ('fibre_g', 'Ballaststoffe (g)'), ('nutri_points', 'Nutri-Score Punkte'), ('nutri_class', 'Nutri-Score Klasse')], default='weight_g', max_length=23)),
                ('recipe_type', models.CharField(blank=True, choices=[('breakfast', 'Frühstück'), ('warm_meal', 'Warme Malzeit'), ('cold_meal', 'Kalte Malzeit'), ('dessert', 'Nachtisch'), ('side_dish', 'Beilage'), ('snack', 'Snack'), ('drink', 'Getränk'), ('ingredient', 'Zutat'), ('sub_recipe', 'Unter Rezept')], default='warm_meal', help_text='Recipe type this hint applies to (if specific)', max_length=11, null=True)),
                ('recipe_objective', models.CharField(blank=True, choices=[('health', 'Gesundheit'), ('taste', 'Geschmack'), ('cost', 'Kosten'), ('fullfillment', 'Sättigung')], default='health', help_text='Recipe objective this hint applies to (if specific)', max_length=20, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='ingredient',
            name='intolerances',
        ),
        migrations.RemoveField(
            model_name='mealeventtemplate',
            name='intolerances',
        ),
        migrations.AddField(
            model_name='ingredient',
            name='durability_in_days',
            field=models.IntegerField(blank=True, default=0, help_text='Durability in days. 0 = unknown, 1-365 = days, >365 = years', null=True),
        ),
        migrations.AddField(
            model_name='ingredient',
            name='is_unprepaired_consumable',
            field=models.BooleanField(default=False, help_text='Indicates if this ingredient is as snack consumable without preparation'),
        ),
        migrations.AddField(
            model_name='ingredient',
            name='managed_by',
            field=models.ManyToManyField(blank=True, related_name='ingredients_managed', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='ingredient',
            name='max_storage_temperature',
            field=models.IntegerField(blank=True, default=20, null=True),
        ),
        migrations.AddField(
            model_name='ingredient',
            name='nova_score',
            field=models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(4)]),
        ),
        migrations.AddField(
            model_name='ingredient',
            name='standard_recipe_weight_g',
            field=models.FloatField(blank=True, default=100, help_text='Default weight in grams used in a standard recipe', null=True),
        ),
        migrations.AddField(
            model_name='recipe',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='recipe',
            name='recipe_ref',
            field=models.ForeignKey(blank=True, help_text='Reference to the orgignal recipe if this is a modified version', null=True, on_delete=django.db.models.deletion.PROTECT, to='food.recipe'),
        ),
        migrations.AddField(
            model_name='recipeitem',
            name='sub_recipe',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='used_in_recipes', to='food.recipe'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='recipe_type',
            field=models.CharField(choices=[('breakfast', 'Frühstück'), ('warm_meal', 'Warme Malzeit'), ('cold_meal', 'Kalte Malzeit'), ('dessert', 'Nachtisch'), ('side_dish', 'Beilage'), ('snack', 'Snack'), ('drink', 'Getränk'), ('ingredient', 'Zutat'), ('sub_recipe', 'Unter Rezept')], default='warm_meal', max_length=11),
        ),
        migrations.AlterField(
            model_name='recipeitem',
            name='portion',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='recipe_items', to='food.portion'),
        ),
        migrations.DeleteModel(
            name='Intolerance',
        ),
    ]
