from django import forms
from django.utils.translation import gettext_lazy as _
from django.forms import ModelForm
from anmelde_tool.event.basic.models import Event, EventModule
from anmelde_tool.attributes.models import AttributeModule
from anmelde_tool.registration.models import Registration
from anmelde_tool.attributes.choices import TravelType, AttributeType

from .models import Registration


class RegistrationListFilter(forms.Form):
    """
    Filter form for EventListView
    """

    name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": _("Nach Namen suchen")}),
    )


class RegistrationBaseForm(forms.ModelForm):
    """
    Base form for all registration forms.
    """

    class Meta:
        model = Registration
        fields = "__all__"  # To be set in subclasses


class DynamicModuleForm(forms.Form):
    """
    Dynamic form for event modules that includes all connected attribute modules
    """

    def __init__(self, *args, **kwargs):
        event_module = kwargs.pop("event_module", None)
        super(DynamicModuleForm, self).__init__(*args, **kwargs)

        if event_module:
            # Get all attribute modules connected to this event module
            attribute_modules = AttributeModule.objects.filter(
                event_module=event_module
            )


            for attribute_module in attribute_modules:
                field_name = f"attribute_{attribute_module.id}"
                field_label = attribute_module.title

                # Create different form fields based on attribute_module type
                if attribute_module.field_type == "StA":
                    self.fields[field_name] = forms.CharField(
                        label=field_label,
                        required=attribute_module.is_required,
                        widget=forms.TextInput(attrs={"placeholder": field_label}),
                        help_text=attribute_module.text,

                    )
                elif attribute_module.field_type == "InA":
                    self.fields[field_name] = forms.IntegerField(
                        label=field_label,
                        required=attribute_module.is_required,
                        widget=forms.NumberInput(attrs={"min": 0}),
                        help_text=attribute_module.text,
                    )
                elif attribute_module.field_type == "BoA":
                    self.fields[field_name] = forms.BooleanField(
                        label=field_label,
                        required=attribute_module.is_required,
                        widget=forms.CheckboxInput(),
                        help_text=attribute_module.text,
                    )
                elif attribute_module.field_type == "TiA":
                    self.fields[field_name] = forms.DateTimeField(
                        label=field_label,
                        required=attribute_module.is_required,
                        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
                        help_text=attribute_module.text,
                    )
                elif attribute_module.field_type == "FlA":
                    self.fields[field_name] = forms.FloatField(
                        label=field_label,
                        required=attribute_module.is_required,
                        widget=forms.NumberInput(attrs={"step": "any"}),
                        help_text=attribute_module.text,
                    )
                elif attribute_module.field_type == "TrA":
                    self.fields[field_name] = forms.ChoiceField(
                        label=field_label,
                        required=attribute_module.is_required,
                        choices=TravelType.choices,
                        widget=forms.Select(),
                        help_text="Travel Type",
                    )
                    # Additional fields for travel attribute
                    num_field_name = f"{field_name}_number_persons"
                    date_field_name = f"{field_name}_date_time"
                    desc_field_name = f"{field_name}_description"

                    self.fields[num_field_name] = forms.IntegerField(
                        label=_("Anzahl der Personen"),
                        required=attribute_module.is_required,
                        min_value=0,
                        widget=forms.NumberInput(attrs={"min": 0}),
                        help_text=_("Gesamtanzahl der Personen, die mit diesem Transportmittel reisen"),
                    )
                    self.fields[date_field_name] = forms.DateTimeField(
                        label=_("Reisezeitpunkt"),
                        required=attribute_module.is_required,
                        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
                        help_text=_("Datum und Uhrzeit der An- oder Abreise"),
                    )
                    self.fields[desc_field_name] = forms.CharField(
                        label=_("Zusätzliche Informationen"),
                        required=False,
                        max_length=100,
                        widget=forms.TextInput(attrs={"placeholder": _("Details zur Reise")}),
                        help_text=_("Weitere Angaben zum Transport (z.B. Treffpunkt, Zugnummer)"),
                    )


def create_module_form_class(event_module):
    """
    Factory function to create a form class for a specific event module
    """
    class_name = f"EventModule{event_module.id}Form"
    return type(class_name, (DynamicModuleForm,), {})
