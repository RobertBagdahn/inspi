from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, HTML, Div
from .choices import ScoutOrganisationLevelChoices
from ckeditor.widgets import CKEditorWidget
from .models import ScoutHierarchy, ZipCode
from django.core.exceptions import ValidationError


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
