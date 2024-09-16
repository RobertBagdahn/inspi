from django import forms

from .choices import SuitLevel, WarmMeal, AnimalProducts, MealTimeOptions, ChildFrendly
from .models import MealEventTemplate


class MealEventForm(forms.Form):
    title = forms.CharField(
        label="Titel des Artikels",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        help_text="Das ist der Haupttitel des Artikels",
    )
    description = forms.CharField(
        label="Beschreibung",
        required=True,
        widget=forms.Textarea(attrs={"class": "form-control"}),
        help_text="Das ist die Beschreibung des Artikels",
    )
    max_price = forms.DecimalField(
        label="Maximaler Preis",
        required=True,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
        help_text="Das ist der maximale Preis, den Sie für das Essen ausgeben möchten",
    )


class SearchForm(forms.Form):
    query = forms.CharField(
        label="Suche",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        help_text="Suchen Sie nach einer Zutaz",
    )
    physical_viscosity = forms.CharField(widget=forms.HiddenInput())


class IngredientFilterForm(forms.Form):
    physical_viscosity = forms.ChoiceField(
        label="Viskosität",
        required=False,
        choices=[
            ("", "Alle"),
            ("liquid", "Flüssig"),
            ("solid", "Fest"),
        ],
        widget=forms.RadioSelect(
            attrs={"class": "tailwind-radio", "onchange": "submit();"}
        ),
    )
    # add hidden query
    query = forms.CharField(widget=forms.HiddenInput())

class MealEventTemplateForm(forms.ModelForm):
    name = forms.CharField(
        label="Name",
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"class": "tailwind-input"}),
    )
    description = forms.CharField(
        label="Description",
        max_length=255,
        required=False,
        widget=forms.Textarea(attrs={"class": "tailwind-textarea"}),
    )
    max_price_eur = forms.FloatField(
        label="Max Price (EUR)",
        required=False,
        widget=forms.NumberInput(attrs={"class": "tailwind-input"}),
    )
    is_public = forms.BooleanField(
        label="Is Public",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "tailwind-checkbox"}),
    )
    suit_level = forms.ChoiceField(
        label="Suit Level",
        required=False,
        choices=SuitLevel.choices,
        widget=forms.RadioSelect(attrs={"class": "tailwind-radio", "onchange": "submit();"}),
    )
    warm_meal = forms.ChoiceField(
        label="Warm Meal",
        required=False,
        choices=WarmMeal.choices,
        widget=forms.RadioSelect(attrs={"class": "tailwind-radio", "onchange": "submit();"}),
    )
    animal_products = forms.ChoiceField(
        label="Animal Products",
        required=False,
        choices=AnimalProducts.choices,
        widget=forms.RadioSelect(attrs={"class": "tailwind-radio", "onchange": "submit();"}),
    )
    meal_time_options = forms.ChoiceField(
        label="Meal Time Options",
        required=False,
        choices=MealTimeOptions.choices,
        widget=forms.RadioSelect(attrs={"class": "tailwind-radio", "onchange": "submit();"}),
    )
    child_frendly = forms.ChoiceField(
        label="Child Friendly",
        required=False,
        choices=ChildFrendly.choices,
        widget=forms.RadioSelect(attrs={"class": "tailwind-radio", "onchange": "submit();"}),
    )

    class Meta:
        model = MealEventTemplate
        fields = [
            'name',
            'description',
            'max_price_eur',
            'is_public',
            'suit_level',
            'warm_meal',
            'animal_products',
            'meal_time_options',
            'child_frendly',
        ]
