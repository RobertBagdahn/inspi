from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, HTML, Div
from .choices import ScoutOrganisationLevelChoices, StateChoices
from ckeditor.widgets import CKEditorWidget
from .models import ScoutHierarchy, ZipCode, NutritionalTag, EventLocation
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model


class ScoutHierarchySearchForm(forms.Form):
    query = forms.CharField(
        label="Suche",
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Suchbegriff eingeben"}
        ),
    )
    level = forms.ChoiceField(
        label="Ebene",
        choices=[("", "Alle")] + ScoutOrganisationLevelChoices.choices,
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    status = forms.ChoiceField(
        label="Status",
        choices=[

            ("active", "Aktiv"),
            ("", "Alle"),
            ("inactive", "Inaktiv"),
            ("upcoming", "Zukünftig")

        ],
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ScoutHierarchyForm(forms.ModelForm):
    name = forms.CharField(
        label="Kurzname",
        max_length=14,
        required=True,
        help_text="Ein kurzer Name deiner Organisation mit maximal 14 Zeichen.",
    )
    abbreviation = forms.CharField(
        label="Abkürzung",
        max_length=5,
        required=False,
        help_text="Eine Extrem kurze Abkürzung mit maximal 5 Zeichen.",
    )
    full_name = forms.CharField(
        label="Voller Name",
        max_length=200,
        required=False,
        help_text="Der vollstänige Name.",
    )
    description = forms.CharField(
        label="Inhalt des Artikels",
        widget=CKEditorWidget(attrs={"class": "col-span-2"}),
        max_length=1000,
        required=False,
        help_text="Beschreibung mit allen Details. Links oder andere Quellen.",
    )
    level_choice = forms.ChoiceField(
        label="Ebene",
        choices=ScoutOrganisationLevelChoices.choices,
        required=True,
        initial=ScoutOrganisationLevelChoices.STAMM,
        help_text="Wähle die richtige Ebene",
    )
    zip_code = forms.ModelChoiceField(
        label="Postleitzahl",
        queryset=ZipCode.objects.all().order_by("zip_code"),
        required=False,
        help_text="Postzeitzahl wo deine Orgnisation auf der Karte dargestellt wird.",
    )
    parent = forms.ModelChoiceField(
        label="Überorganisation",
        queryset=ScoutHierarchy.objects.all(),
        required=True,
        help_text="",
    )
    exist_from = forms.DateField(
        label="Gründungsdatum",
        widget=forms.DateInput(
            format="%Y-%m-%d", attrs={"class": "form-control", "type": "date"}
        ),
        required=False,
        help_text="Datum seit dem es die Organisation gibt.",
    )
    exist_till = forms.DateField(
        label="Auflösungsdatum",
        widget=forms.DateInput(
            format="%Y-%m-%d", attrs={"class": "form-control", "type": "date"}
        ),
        required=False,
        help_text="Datum bis zu dem es die Organisation gab.",
    )

    def clean(self):
        cleaned_data = super().clean()
        level_choice = cleaned_data.get("level_choice")
        parent = cleaned_data.get("parent")

        if parent:
            parent_level_choice = parent.level_choice
            valid_choices = {
                "Verband": ["Bund"],
                "Bund": ["Ring", "Stamm"],
                "Ring": ["Stamm"],
                "Stamm": ["Gruppe"],
            }

            if level_choice not in valid_choices.get(parent_level_choice, []):
                raise ValidationError(
                    f"Ungültige Ebene: {level_choice} kann nicht unter {parent_level_choice} existieren."
                )

        return cleaned_data

    class Meta:
        model = ScoutHierarchy
        exclude = ["created_at", "slug", "status"]


class ZipCodeForm(forms.ModelForm):
    zip_code = forms.CharField(
        label="Postleitzahl",
        max_length=5,
        required=True,
        help_text="5-stellige Postleitzahl",
    )
    city = forms.CharField(
        label="Stadt",
        max_length=60,
        required=True,
        help_text="Name der Stadt",
    )
    lat = forms.DecimalField(
        label="Breitengrad",
        max_digits=20,
        decimal_places=15,
        required=False,
        help_text="Breitengrad der Koordinaten",
    )
    lon = forms.DecimalField(
        label="Längengrad",
        max_digits=20,
        decimal_places=15,
        required=False,
        help_text="Längengrad der Koordinaten",
    )
    state = forms.ChoiceField(
        label="Bundesland",
        choices=StateChoices.choices,
        required=True,
        help_text="Bundesland der PLZ",
    )

    class Meta:
        model = ZipCode
        exclude = ["created_at", "updated_at"]


class ZipCodeSearchForm(forms.Form):
    query = forms.CharField(
        label="Suche",
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "PLZ oder Stadt eingeben"}
        ),
    )
    state = forms.ChoiceField(
        label="Bundesland",
        choices=[("", "Alle")] + list(StateChoices.choices),
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class NutritionalTagForm(forms.ModelForm):
    name = forms.CharField(
        label="Name",
        max_length=255,
        required=True,
        help_text="Name des Tags. Z.B. 'Fleisch', 'Alkohol', 'Nüsse', 'Scharf'",
    )
    name_opposite = forms.CharField(
        label="Gegenteiliger Name",
        max_length=255,
        required=True,
        help_text="Name des Tags für menschenlesbare Ausgabe. z.B. 'Vegan', 'Vegetarisch', 'Alkoholfrei'",
    )
    description = forms.CharField(
        label="Beschreibung aus sicht der Zutat",
        max_length=255,
        required=True,
    )
    description_human = forms.CharField(
        label="Beschreibung aus sicht des Menschen, der das nicht essen kann",
        max_length=255,
        required=True,
    )
    rank = forms.IntegerField(
        label="Rangfolge",
        initial=1,
        required=True,
    )
    is_dangerous = forms.BooleanField(
        label="Gefährlich",
        required=False,
        help_text="Gibt an, ob dieser Tag eine potenziell schädliche oder gefährliche Zutat darstellt",
    )
    default_in_event = forms.BooleanField(
        label="Standard in Veranstaltungen",
        required=False,
        help_text="Gibt an, ob dieser Tag automatisch in der Veranstaltung enthalten ist",
    )

    class Meta:
        model = NutritionalTag
        exclude = ["created_at", "updated_at"]


class EventLocationForm(forms.ModelForm):
    name = forms.CharField(
        label="Name",
        max_length=60,
        required=True,
        help_text="Name des Veranstaltungsortes"
    )
    description = forms.CharField(
        label="Beschreibung",
        max_length=200,
        required=False,
        help_text="Kurze Beschreibung des Veranstaltungsortes"
    )
    address = forms.CharField(
        label="Adresse",
        max_length=60,
        required=False,
        help_text="Straße und Hausnummer des Veranstaltungsortes"
    )
    zip_code = forms.ModelChoiceField(
        label="Postleitzahl",
        queryset=ZipCode.objects.all().order_by('zip_code'),
        required=False,
        help_text="PLZ des Veranstaltungsortes"
    )
    contact_name = forms.CharField(
        label="Kontaktperson",
        max_length=30,
        required=False,
        help_text="Name der Ansprechperson"
    )
    contact_email = forms.CharField(
        label="E-Mail",
        max_length=30,
        required=False,
        help_text="E-Mail-Adresse der Kontaktperson"
    )
    contact_phone = forms.CharField(
        label="Telefonnummer",
        max_length=30,
        required=False,
        help_text="Telefonnummer der Kontaktperson"
    )
    per_person_fee = forms.FloatField(
        label="Gebühr pro Person",
        required=False,
        help_text="Preis pro Person (falls zutreffend)"
    )
    fix_fee = forms.FloatField(
        label="Fixgebühr",
        required=False,
        help_text="Fixe Gebühr für die Nutzung des Ortes"
    )

    class Meta:
        model = EventLocation
        exclude = ["created_at", "updated_at"]


class EventLocationSearchForm(forms.Form):
    query = forms.CharField(
        label="Suche",
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Name oder Ort eingeben"}
        ),
    )
    state = forms.ChoiceField(
        label="Bundesland",
        choices=[("", "Alle")] + list(StateChoices.choices),
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class NutritionalTagSearchForm(forms.Form):
    query = forms.CharField(
        label="Suche",
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Besonderheiten suchen"}
        ),
    )
    is_dangerous = forms.ChoiceField(
        label="Gefährlich",
        choices=[("", "Alle"), ("True", "Ja"), ("False", "Nein")],
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )


class UserSearchForm(forms.Form):
    query = forms.CharField(
        label="Suche",
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Name, E-Mail oder Benutzername eingeben"}
        ),
    )
    user_type = forms.ChoiceField(
        label="Benutzertyp",
        choices=[
            ("", "Alle"),
            ("staff", "Mitarbeiter"),
            ("superuser", "Administrator"),
            ("active", "Aktiv"),
            ("inactive", "Inaktiv"),
        ],
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.layout = Layout(
            Div(
                Div('query', css_class='col-md-5'),
                Div('user_type', css_class='col-md-5'),
                Div(Submit('submit', 'Suchen', css_class='btn btn-primary'), css_class='col-md-2'),
                css_class='row'
            )
        )