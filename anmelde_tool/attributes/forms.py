from django import forms
from .models import AttributeType
from .models import (
    BooleanAttribute,
    DateTimeAttribute,
    IntegerAttribute,
    FloatAttribute,
    StringAttribute,
    TravelAttribute,
    AttributeModule
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


class TravelAttributeForm(forms.ModelForm):
    class Meta:
        model = TravelAttribute
        fields = ["number_persons", "type_field", "date_time_field", "description"]
        widgets = {
            "date_time_field": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "description": forms.TextInput(),
        }


class GeneralAttributeForm(forms.ModelForm):
    """
    General form for all attribute types.
    """
    
    field_type = forms.ChoiceField(
        choices=AttributeType.choices,
        widget=forms.Select(),
        required=True,
        label="Attribute Type"
    )
    title = forms.CharField(max_length=1000, required=False)
    text = forms.CharField(widget=forms.Textarea, max_length=10000, required=False)
    is_required = forms.BooleanField(required=False, initial=False)
    default_value = forms.CharField(max_length=1000, required=False)
    max_entries = forms.IntegerField(min_value=1, initial=1)

    
    class Meta:
        model = AttributeModule
        fields = ["field_type", "title", "text", "is_required", "default_value", "max_entries"]