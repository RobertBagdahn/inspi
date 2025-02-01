from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, HTML, Div

from .choices import (
    SuitLevel,
    WarmMeal,
    AnimalProducts,
    MealTimeOptions,
    ChildFrendly,
    PhysicalViscosityChoices,
    RetailerTypeChoise,
    BrandQualityChoises,
    IntoleranceChoices,
    MealEventTemplateOptionsChoices,
    RecipeType,
    IngredientStatus,
    MealType,
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
    Meal,
    MealDay,
    MealItem,
    RetailSection,
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
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Suchbegriff eingeben"}
        ),
    )
    physical_viscosity = forms.ChoiceField(
        label="Viskosität",
        required=False,
        choices=[(None, "Alle")] + list(PhysicalViscosityChoices.choices),
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    retail_section = forms.ChoiceField(
        label="Supermarkt Kategorie",  # RetailSection
        choices=[(None, "Alle")]
        + [(rs.id, rs.name) for rs in RetailSection.objects.all()],
        required=False,
        widget=forms.Select(attrs={"class": "tailwind-select"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "",
                Div(
                    Div("query", css_class="col-md-6"),
                    Div("physical_viscosity", css_class="col-md-3"),
                    Div("retail_section", css_class="col-md-3"),
                    css_class="grid grid-cols-3 gap-2",
                ),
            ),
            Submit(
                "submit",
                "Suchen",
                css_class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded",
            ),
        )


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
            "meal_time_options",
            "child_frendly",
            "intolerances",
            "template_options",
        ]


class IngredientFormCopy(forms.Form):
    name = forms.CharField(
        label="Name der Zutat",
        max_length=40,
        required=True,
        widget=forms.TextInput(attrs={"class": "tailwind-input"}),
    )
    description = forms.CharField(
        label="Beschreibung",
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"class": "tailwind-input"}),
    )
    query = forms.CharField(
        label="Filter für Basis Zutat",
        max_length=40,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "tailwind-input",
                "placeholder": "Suchbegriff eingeben",
                "hx-trigger": "keyup delay:500ms",
                "hx-get": "/food/ingredients/autocomplete",
                "hx-target": "#id_ingredient_ref",
            }
        ),
    )
    ingredient_ref = forms.ModelChoiceField(
        label="Basis Zutat",
        required=True,
        queryset=Ingredient.objects.all(),
        initial=Ingredient.objects.first(),
        widget=forms.Select(
            attrs={"class": "tailwind-select", "id": "id_ingredient_ref"}
        ),
        help_text="Wählen Sie die Zutat aus, die kopiert werden soll.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class IngredientFormAi(forms.Form):
    name = forms.CharField(
        label="Name der Zutat",
        max_length=40,
        required=False,
        widget=forms.TextInput(attrs={"class": "tailwind-input"}),
        help_text="Name des Lebensmittels",
    )
    description = forms.CharField(
        label="Beschreibung",
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"class": "tailwind-input"}),
        help_text="Beschreibung des Lebensmittels, welches die KI erzeugt soll.",
    )


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
        initial=PhysicalViscosityChoices.SOLID,
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
    retail_section = forms.ChoiceField(
        label="Supermarkt Kategorie",  # RetailSection
        choices=[(None, "Alle")]
        + [(rs.id, rs.name) for rs in RetailSection.objects.all()],
        required=False,
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
        widget=forms.CheckboxSelectMultiple(attrs={"class": "tailwind-checkbox"}),
        help_text="Wählen Sie die möglichen Portionen für dieses Lebensmittel aus. Weitere sind später auch noch hinzufügbar.",
    )
    intolerances = forms.MultipleChoiceField(
        label="Unverträglichkeiten",
        required=False,
        choices=IntoleranceChoices.choices,
        widget=forms.CheckboxSelectMultiple(),
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


class IngredientFormUpdateBasic(forms.ModelForm):

    name = forms.CharField(
        label="Name der Zutat",
        max_length=40,
        required=False,
        widget=forms.TextInput(attrs={"class": "tailwind-input"}),
        help_text="Name des Lebensmittels",
    )
    description = forms.CharField(
        label="Beschreibung",
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"class": "tailwind-input"}),
        help_text="Beschreibung des Lebensmittels",
    )
    retail_section = forms.ChoiceField(
        label="Supermarkt Kategorie",  # RetailSection
        choices=[(None, "Alle")]
        + [(rs.id, rs.name) for rs in RetailSection.objects.all()],
        required=False,
        widget=forms.Select(attrs={"class": "tailwind-select"}),
    )
    status = forms.ChoiceField(
        label="Status",
        required=False,
        choices=IngredientStatus.choices,
        widget=forms.Select(attrs={"class": "tailwind-select"}),
        help_text="Status der Veröffentlichung",
    )

    class Meta:
        model = Ingredient
        fields = ["name", "description", "retail_section", "status"]


class IngredientFormUpdateAttribute(forms.ModelForm):

    intolerances = forms.ModelMultipleChoiceField(
        label="Unverträglichkeiten",
        required=False,
        queryset=Intolerance.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
    )

    physical_density = forms.FloatField(
        label="Dichte des Lebensmittels",
        required=False,
        widget=forms.NumberInput(attrs={"class": "tailwind-input"}),
        initial=1.0,
        help_text="Dichte in der Einheit g/cm³ oder Kg/l",
    )
    physical_viscosity = forms.ChoiceField(
        label="Essen oder Getränk",
        required=True,
        initial=PhysicalViscosityChoices.SOLID,
        choices=PhysicalViscosityChoices.choices,
        widget=forms.RadioSelect(attrs={"class": "tailwind-radio"}),
        help_text="Festes oder flüssiges Lebensmittel",
    )
    child_frendly_score = forms.IntegerField(
        widget=forms.NumberInput(attrs={"class": "tailwind-input"}),
        label="Kinderfreundlich",
        required=True,
        help_text="Werte von 1 bis 5"
        "1 = nicht kinderfreundlich"
        "5 = sehr kinderfreundlich",
        max_value=5,
        min_value=1,
    )
    scout_frendly_score = forms.IntegerField(
        widget=forms.NumberInput(attrs={"class": "tailwind-input"}),
        label="Pfadfinderfreundlich",
        required=True,
        help_text="Werte von 1 bis 5. 1 = nicht pfadfinderfreundlich, 5 = sehr pfadfinderfreundlich",
        max_value=5,
        min_value=1,
    )

    class Meta:
        model = Ingredient
        fields = [
            "intolerances",
            "physical_density",
            "physical_viscosity",
            "child_frendly_score",
            "scout_frendly_score",
        ]


class IngredientFormUpdateRef(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = [
            "fdc_id",
            "nan_art_id_rewe",
            "ean",
            "ingredient_ref",
        ]
        widgets = {
            "fdc_id": forms.NumberInput(attrs={"class": "tailwind-input"}),
            "nan_art_id_rewe": forms.NumberInput(attrs={"class": "tailwind-input"}),
            "ean": forms.NumberInput(attrs={"class": "tailwind-input"}),
            "ingredient_ref": forms.Select(attrs={"class": "tailwind-select"}),
        }


class IngredientFormUpdateNutrition(forms.ModelForm):
    class Meta:
        model = MetaInfo
        fields = [
            "energy_kj",
            "protein_g",
            "fat_g",
            "fat_sat_g",
            "sodium_mg",
            "carbohydrate_g",
            "sugar_g",
            "fibre_g",
            "fruit_factor",
        ]
        widgets = {
            "energy_kj": forms.NumberInput(attrs={"class": "tailwind-input"}),
            "protein_g": forms.NumberInput(attrs={"class": "tailwind-input"}),
            "fat_g": forms.NumberInput(attrs={"class": "tailwind-input"}),
            "fat_sat_g": forms.NumberInput(attrs={"class": "tailwind-input"}),
            "sodium_mg": forms.NumberInput(attrs={"class": "tailwind-input"}),
            "carbohydrate_g": forms.NumberInput(attrs={"class": "tailwind-input"}),
            "sugar_g": forms.NumberInput(attrs={"class": "tailwind-input"}),
            "fibre_g": forms.NumberInput(attrs={"class": "tailwind-input"}),
            "fruit_factor": forms.NumberInput(attrs={"class": "tailwind-input"}),
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
    name = forms.CharField(
        label="Name",
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={"class": "tailwind-input"}),
    )
    description = forms.CharField(
        label="Beschreibung",
        required=True,
        widget=forms.Textarea(attrs={"class": "tailwind-textarea"}),
    )
    recipe_type = forms.ChoiceField(
        label="Rezept Typ",
        required=True,
        choices=RecipeType.choices,
        widget=forms.Select(attrs={"class": "tailwind-select"}),
    )

    class Meta:
        model = Recipe
        fields = [
            "name",
            "description",
            "recipe_type",
        ]


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


class MealForm(forms.ModelForm):
    meal_day = forms.ModelChoiceField(
        queryset=MealDay.objects.all(),
        widget=forms.HiddenInput(),
    )
    meal_type = forms.ChoiceField(
        label="Typ der Mahlzeit",
        choices=MealType.choices,
        widget=forms.Select(attrs={"class": "tailwind-select"}),
    )
    day_part_factor = forms.FloatField(
        label="Prozent der Tagesättigung",
        widget=forms.NumberInput(attrs={"class": "tailwind-input"}),
    )
    name = forms.CharField(
        label="Name (optional)",
        help_text="Wenn kein Name vergeben wird, dann wird der Mahlzeittyp verwendet.",
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"class": "tailwind-input"}),
    )
    time_start = forms.TimeField(
        label="Start Zeit",
        widget=forms.TimeInput(
            format="%H:%M", attrs={"class": "tailwind-input", "type": "time"}
        ),
    )
    time_end = forms.TimeField(
        label="End Zeit",
        widget=forms.TimeInput(
            format="%H:%M", attrs={"class": "tailwind-input", "type": "time"}
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        time_start = cleaned_data.get("time_start")
        time_end = cleaned_data.get("time_end")

        if time_start and time_end and time_end <= time_start:
            self.add_error("time_end", "End time must be later than start time.")

    class Meta:
        model = Meal
        fields = [
            "meal_day",
            "meal_type",
            "day_part_factor",
            "time_start",
            "time_end",
            "name",
        ]


class MealDayForm(forms.ModelForm):
    class Meta:
        model = MealDay
        fields = ["date"]


class MealItemFormCreate(forms.ModelForm):
    meal = forms.ModelChoiceField(
        queryset=Meal.objects.all(),
        widget=forms.HiddenInput(),
    )
    recipe = forms.ModelChoiceField(
        queryset=Recipe.objects.all(),
    )
    factor = forms.FloatField(
        widget=forms.NumberInput(attrs={"class": "tailwind-input"}),
    )

    class Meta:
        model = MealItem
        fields = [
            "meal",
            "recipe",
            "factor",
        ]


class MealItemFormUpdate(forms.ModelForm):
    class Meta:
        model = MealItem
        fields = [
            "meal",
            "recipe",
            "factor",
        ]
        widgets = {
            "meal": forms.HiddenInput(),
            "recipe": forms.Select(attrs={"class": "tailwind-select"}),
            "factor": forms.NumberInput(attrs={"class": "tailwind-input"}),
        }


class SearchRecipeForm(forms.Form):
    query = forms.CharField(
        label="Suche",
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Suchbegriff eingeben"}
        ),
    )
    recipe_type = forms.ChoiceField(
        label="Rezept Typ",
        required=False,
        choices=[(None, "Alle")] + list(RecipeType.choices),
        widget=forms.Select(attrs={"class": "form-control"}),
    )


class SearchPlanForm(forms.Form):
    query = forms.CharField(
        label="Suche",
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Suchbegriff eingeben"}
        ),
    )
