from django import forms
from django.utils.translation import gettext_lazy as _
from .models import AttributeType
from .models import (
    BooleanAttribute,
    DateTimeAttribute,
    IntegerAttribute,
    FloatAttribute,
    StringAttribute,
    AttributeModule,
    DateAttribute,
    HTMLAttribute,
    RadioAttribute,
    MultiSelectAttribute,
    ZipCodeAttribute,
    EmailAttribute,
    PhoneAttribute,
    ScoutGroupAttribute,
    AttributeChoiceOption,
)


class BooleanAttributeForm(forms.ModelForm):
    class Meta:
        model = BooleanAttribute
        fields = ["boolean_field"]
        widgets = {
            "boolean_field": forms.CheckboxInput(),
        }


class DateTimeAttributeForm(forms.ModelForm):
    class Meta:
        model = DateTimeAttribute
        fields = ["date_time_field"]
        widgets = {
            "date_time_field": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }


class IntegerAttributeForm(forms.ModelForm):
    class Meta:
        model = IntegerAttribute
        fields = ["integer_field"]
        widgets = {
            "integer_field": forms.NumberInput(),
        }


class FloatAttributeForm(forms.ModelForm):
    class Meta:
        model = FloatAttribute
        fields = ["float_field"]
        widgets = {
            "float_field": forms.NumberInput(attrs={"step": "any"}),
        }


class StringAttributeForm(forms.ModelForm):
    class Meta:
        model = StringAttribute
        fields = ["string_field"]
        widgets = {
            "string_field": forms.TextInput(),
        }


class GeneralAttributeForm(forms.ModelForm):
    """
    General form for all attribute types.
    """

    field_type = forms.ChoiceField(
        choices=AttributeType.choices,
        widget=forms.Select(),
        required=True,
        label="Attributtyp",
        help_text="Hier können Sie den Typ des Attributs auswählen.",
    )
    title = forms.CharField(
        max_length=1000,
        required=False,
        label="Titel",
        help_text="Hier können Sie den Titel des Attributs eingeben.",
    )
    text = forms.CharField(
        widget=forms.Textarea,
        max_length=10000,
        required=False,
        label="Text",
        help_text="Hier können Sie eine Beschreibung des Attributs eingeben.",
    )
    is_required = forms.BooleanField(
        required=False,
        initial=False,
        label="Pflichtfeld",
        help_text="Das Attribut ist ein Pflichtfeld.",
    )

    class Meta:
        model = AttributeModule
        fields = [
            "field_type",
            "title",
            "text",
            "is_required",
        ]


class DateAttributeForm(forms.ModelForm):
    class Meta:
        model = DateAttribute
        fields = ["date_field"]
        widgets = {
            "date_field": forms.DateInput(attrs={"type": "date"}),
        }


class HTMLAttributeForm(forms.ModelForm):
    class Meta:
        model = HTMLAttribute
        fields = ["html_field"]
        widgets = {
            "html_field": forms.Textarea(),
        }


class RadioAttributeForm(forms.ModelForm):
    class Meta:
        model = RadioAttribute
        fields = ["selected_option"]


class MultiSelectAttributeForm(forms.ModelForm):
    class Meta:
        model = MultiSelectAttribute
        fields = ["selected_options"]
        widgets = {"selected_options": forms.MultipleChoiceField()}


class ZipCodeAttributeForm(forms.ModelForm):
    class Meta:
        model = ZipCodeAttribute
        fields = ["zip_code_field"]
        widgets = {
            "zip_code_field": forms.TextInput(),
        }


class EmailAttributeForm(forms.ModelForm):
    class Meta:
        model = EmailAttribute
        fields = ["email_field"]
        widgets = {
            "email_field": forms.EmailInput(),
        }


class PhoneAttributeForm(forms.ModelForm):
    class Meta:
        model = PhoneAttribute
        fields = ["phone_number_field"]
        widgets = {
            "phone_number_field": forms.TextInput(),
        }


class ScoutGroupAttributeForm(forms.ModelForm):
    class Meta:
        model = ScoutGroupAttribute
        fields = ["scout_group"]
        widgets = {
            "scout_group": forms.Select(),
        }


class AttributeChoiceOptionForm(forms.ModelForm):
    class Meta:
        model = AttributeChoiceOption
        fields = ["text", "ordering"]
        widgets = {
            "text": forms.TextInput(
                attrs={
                    "class": "block w-full mt-1 rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
                }
            ),
            "ordering": forms.NumberInput(
                attrs={
                    "class": "block w-full mt-1 rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
                }
            ),
        }
        labels = {
            "text": _("Text"),
            "ordering": _("Reihenfolge"),
        }
        help_texts = {
            "text": _("Text der Auswahloption"),
            "ordering": _(
                "Position in der Liste (niedrigere Zahlen erscheinen zuerst)"
            ),
        }
