from django import forms


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
