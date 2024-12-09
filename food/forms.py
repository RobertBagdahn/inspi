from django import forms

from .choices import (
    SuitLevel,
    WarmMeal,
    AnimalProducts,
    MealTimeOptions,
    ChildFrendly,
    PhysicalViscosityChoices,
    FoodMajorClasses,
    RetailerTypeChoise,
    BrandQualityChoises,
    IntoleranceChoices,
    MealEventTemplateOptionsChoices,
    RecipeType,
)
from .models import (
    MealEventTemplate,
    MeasuringUnit,
    Portion,
    Price,
    Recipe,
    RecipeItem,
    Intolerance,
    TemplateOption,
    Ingredient,
    MetaInfo,
)

from general.login.models import CustomUser


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


class MealEventTemplateFormCreate(forms.Form):
    name = forms.CharField(
        label="Name der Veranstaltung",
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"class": "tailwind-input"}),
    )
    description = forms.CharField(
        label="Beschreibung deiner Veranstaltung",
        max_length=255,
        required=False,
        widget=forms.Textarea(attrs={"class": "tailwind-textarea"}),
    )
    max_price_eur = forms.FloatField(
        label="Max Preis je Tag (EUR)",
        required=False,
        widget=forms.NumberInput(attrs={"class": "tailwind-input"}),
        help_text="Das ist der maximale Preis, den du pro Tag und Person für das Essen ausgeben möchten",
    )
    meal_time_options = forms.ChoiceField(
        label="Wie lange soll die Veranstaltung dauern?",
        required=False,
        choices=MealTimeOptions.choices,
        widget=forms.RadioSelect(attrs={"class": "tailwind-radio"}),
    )
    suit_level = forms.ChoiceField(
        label="Süßigkeitsstufe",
        required=False,
        choices=SuitLevel.choices,
        widget=forms.RadioSelect(attrs={"class": "tailwind-radio"}),
        help_text="Wieviel Süßigkeiten soll es auf der Veranstaltung geben?",
    )
    warm_meal = forms.ChoiceField(
        label="Warme Mahlzeiten",
        required=False,
        choices=WarmMeal.choices,
        widget=forms.RadioSelect(attrs={"class": "tailwind-radio"}),
        help_text="Soll es warme Mahlzeiten geben?",
    )
    animal_products = forms.ChoiceField(
        label="Tierische Produkte",
        required=False,
        choices=AnimalProducts.choices,
        widget=forms.RadioSelect(attrs={"class": "tailwind-radio"}),
    )
    child_frendly = forms.ChoiceField(
        label="Zielgruppe?",
        required=False,
        choices=ChildFrendly.choices,
        widget=forms.RadioSelect(attrs={"class": "tailwind-radio"}),
        help_text="Ist die Veranstaltung für Kinder geeignet?",
    )
    intolerances = forms.MultipleChoiceField(
        label="Unverträglichkeiten",
        required=False,
        choices=IntoleranceChoices.choices,
        widget=forms.CheckboxSelectMultiple(),
    )
    template_options = forms.MultipleChoiceField(
        label="Template Option",
        required=False,
        choices=MealEventTemplateOptionsChoices.choices,
        widget=forms.CheckboxSelectMultiple(),
    )


class MealEventTemplateFormUpdate(forms.ModelForm):

    class Meta:
        model = MealEventTemplate
        fields = [
            "name",
            "description",
            "max_price_eur",
            "is_public",
            "suit_level",
            "warm_meal",
            "animal_products",
            "meal_time_options",
            "child_frendly",
            "intolerances",
            "template_options",
        ]

class IngredientForm(forms.Form):
    name = forms.CharField(
        label="Name der Zutat",
        max_length=40,
        required=False,
        widget=forms.TextInput(attrs={"class": "tailwind-input"}),
    )
    description = forms.CharField(
        label="Beschreibung",
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"class": "tailwind-input"}),
    )
    physical_density = forms.FloatField(
        label="Dichte des Lebensmittels",
        required=False,
        widget=forms.NumberInput(attrs={"class": "tailwind-input"}),
        initial=1.0,
        help_text="""
            Die Dichte des Lebensmittels in g/cm³.
            Wasser hat die Dichte 1.0.
            Mehl von 0.5 bis 0.6.
            Schokolade von 1.2 bis 1.6.
        """,
    )
    physical_viscosity = forms.ChoiceField(
        label="Fest oder Flüssig",
        required=False,
        initial="solid",
        choices=PhysicalViscosityChoices.choices,
        widget=forms.RadioSelect(attrs={"class": "tailwind-radio"}),
    )
    ingredient_ref = forms.ModelChoiceField(
        label="Ingredient Reference",
        required=False,
        queryset=Ingredient.objects.all(),
        widget=forms.Select(attrs={"class": "tailwind-radio"}),
    )
    fdc_id = forms.IntegerField(
        label="FDC ID",
        required=False,
        widget=forms.NumberInput(attrs={"class": "tailwind-input"}),
    )
    nan_art_id_rewe = forms.IntegerField(
        label="NAN ART ID REWE",
        required=False,
        widget=forms.NumberInput(attrs={"class": "tailwind-input"}),
    )
    ean = forms.IntegerField(
        label="EAN",
        required=False,
        widget=forms.NumberInput(attrs={"class": "tailwind-input"}),
    )
    major_class = forms.ChoiceField(
        label="Major Class",
        required=False,
        choices=FoodMajorClasses.choices,
        widget=forms.Select(attrs={"class": "tailwind-select"}),
    )
    unprepared_eatable = forms.BooleanField(
        label="Unprepared Eatable",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "tailwind-checkbox"}),
    )
    portions = forms.ModelMultipleChoiceField(
        label="Mögliche Portionen",
        required=False,
        queryset=MeasuringUnit.objects.all(),
        widget=forms.CheckboxSelectMultiple(
            attrs={"class": "tailwind-checkbox"}
        ),
        help_text="Wählen Sie die möglichen Portionen für dieses Lebensmittel aus. Weitere sind später auch noch hinzufügbar.",
    )
    intolerances = forms.MultipleChoiceField(
        label="Unverträglichkeiten",
        required=False,
        choices=IntoleranceChoices.choices,
        widget=forms.CheckboxSelectMultiple(),
    )
    animal_products = forms.ChoiceField(
        label="Tierische Produkte",
        required=False,
        choices=AnimalProducts.choices,
        widget=forms.RadioSelect(attrs={"class": "tailwind-radio"}),
    )
    energy_kj = forms.FloatField(
        label="Energie (kJ je 100g)",
        required=False,
        widget=forms.NumberInput(attrs={"class": "tailwind-input"}),
    )
    protein_g = forms.FloatField(
        label="Eiweiß (g je 100g)",
        required=False,
        widget=forms.NumberInput(attrs={"class": "tailwind-input"}),
    )
    fat_g = forms.FloatField(
        label="Fett (g je 100g)",
        required=False,
        widget=forms.NumberInput(attrs={"class": "tailwind-input"}),
    )
    fat_sat_g = forms.FloatField(
        label="Gesättigte Fettsäuren (g je 100g)",
        required=False,
        widget=forms.NumberInput(attrs={"class": "tailwind-input"}),
    )
    sugar_g = forms.FloatField(
        label="Zucker (g je 100g)",
        required=False,
        widget=forms.NumberInput(attrs={"class": "tailwind-input"}),
    )
    salt_g = forms.FloatField(
        label="Salz (g je 100g)",
        required=False,
        widget=forms.NumberInput(attrs={"class": "tailwind-input"}),
    )
    fruit_factor = forms.FloatField(
        label="Fruchtanteil (in %)",
        required=False,
        widget=forms.NumberInput(attrs={"class": "tailwind-input"}),
    )
    carbohydrate_g = forms.FloatField(
        label="Kohlenhydrate (g je 100g)",
        required=False,
        widget=forms.NumberInput(attrs={"class": "tailwind-input"}),
    )
    fibre_g = forms.FloatField(
        label="Balaststoffe (g je 100g)",
        required=False,
        widget=forms.NumberInput(attrs={"class": "tailwind-input"}),
    )



class IngredientFormUpdate(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = [
            "name",
            "description",
            "physical_density",
            "physical_viscosity",
            "ingredient_ref",
            "fdc_id",
            "nan_art_id_rewe",
            "ean",
            "major_class",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "tailwind-input"}),
            "description": forms.TextInput(attrs={"class": "tailwind-input"}),
            "physical_density": forms.NumberInput(attrs={"class": "tailwind-input"}),
            "physical_viscosity": forms.RadioSelect(attrs={"class": "tailwind-radio"}),
            "ingredient_ref": forms.Select(attrs={"class": "tailwind-radio"}),
            "fdc_id": forms.NumberInput(attrs={"class": "tailwind-input"}),
            "nan_art_id_rewe": forms.NumberInput(attrs={"class": "tailwind-input"}),
            "ean": forms.NumberInput(attrs={"class": "tailwind-input"}),
            "major_class": forms.Select(attrs={"class": "tailwind-select"}),
        }


class PortionFormCreate(forms.Form):
    name = forms.CharField(
        label="Name der Portion",
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={"class": "tailwind-input"}),
    )
    measuring_unit = forms.ModelChoiceField(
        label="Messeinheit",
        required=True,
        queryset=MeasuringUnit.objects.all(),
        widget=forms.Select(attrs={"class": "tailwind-select"}),
    )
    quantity = forms.FloatField(
        label="Menge",
        required=True,
        widget=forms.NumberInput(attrs={"class": "tailwind-input"}),
    )
    rank = forms.IntegerField(
        label="Rang",
        required=True,
        widget=forms.NumberInput(attrs={"class": "tailwind-input"}),
    )


class PortionFormUpdate(forms.ModelForm):
    class Meta:
        model = Portion
        fields = [
            "name",
            "measuring_unit",
            "quantity",
            "rank",
        ]


class PriceForm(forms.Form):
    price_eur = forms.FloatField(
        label="Price (EUR)",
        required=False,
        widget=forms.NumberInput(attrs={"class": "tailwind-input"}),
    )
    name = forms.CharField(
        label="Name",
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"class": "tailwind-input"}),
    )
    portion = forms.ModelChoiceField(
        label="Portion",
        required=False,
        queryset=Portion.objects.all(),
        widget=forms.Select(attrs={"class": "tailwind-select"}),
    )
    quantity = forms.FloatField(
        label="Quantity",
        required=False,
        widget=forms.NumberInput(attrs={"class": "tailwind-input"}),
    )
    retailer = forms.ChoiceField(
        label="Retailer",
        required=False,
        choices=RetailerTypeChoise.choices,
        widget=forms.Select(attrs={"class": "tailwind-select"}),
    )
    quality = forms.ChoiceField(
        label="Quality",
        required=False,
        choices=BrandQualityChoises.choices,
        widget=forms.Select(attrs={"class": "tailwind-select"}),
    )


class PriceFormUpdate(forms.ModelForm):
    class Meta:
        model = Price
        fields = [
            "price_eur",
            "name",
            "portion",
            "quantity",
            "retailer",
            "quality",
        ]


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = [
            "name",
            "status",
            "hints",
        ]

class RecipeFormUpdate(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = [
            "name",
            "description",
            "status",
            "recipe_type",
            # "managed_by",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "tailwind-input"}),
            "description": forms.Textarea(attrs={"class": "tailwind-textarea"}),
            "status": forms.Select(attrs={"class": "tailwind-select"}),
            "recipe_type": forms.Select(
                attrs={"class": "tailwind-select"},
                choices=RecipeType.choices,
            ),
            # "managed_by": forms.SelectMultiple(
            #     attrs={"class": "tailwind-select"},
            #     choices=CustomUser.objects.all(),
            # ),
        }


class RecipeItemFormCreate(forms.Form):
    recipe = forms.ModelChoiceField(
        label="Recipe",
        required=True,
        queryset=Recipe.objects.all(),
        widget=forms.HiddenInput(),
    )
    quantity = forms.FloatField(
        label="Quantity",
        required=True,
        initial=1.0,
    )
    portion = forms.ModelChoiceField(
        label="Portion",
        required=True,
        queryset=Portion.objects.all(),
    )


class RecipeItemFormUpdate(forms.Form):
    recipe_item_id = forms.IntegerField(
        label="Recipe Item ID",
        required=True,
        widget=forms.HiddenInput(),
    )
    recipe_id = forms.IntegerField(
        label="Recipe ID",
        required=True,
        widget=forms.HiddenInput(),
    )
    quantity = forms.FloatField(
        label="Quantity",
        required=True,
    )
    portion_id = forms.IntegerField(
        label="Portion ID",
        required=True,
        widget=forms.HiddenInput(),
    )
