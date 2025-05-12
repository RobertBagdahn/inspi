from django import forms
from django.utils.translation import gettext_lazy as _
from django.forms import ModelForm
from anmelde_tool.event.basic.models import Event, EventModule, BookingOption
from anmelde_tool.attributes.models import AttributeModule, AttributeChoiceOption
from anmelde_tool.registration.models import Registration
from anmelde_tool.attributes.choices import TravelType, AttributeType
from masterdata.models import ScoutHierarchy, ZipCode, NutritionalTag
from anmelde_tool.event.basic import choices as event_choices
from general.login.models import Person
from anmelde_tool.registration.choices import DELETION_REASONS
from masterdata.widgets import HtmxAutocompleteWidget


class RegistrationInitialForm(forms.Form):
    """
    Initial form for registration that captures required basic information
    based on the event's registration_type.
    """

    scout_group = forms.ModelChoiceField(
        queryset=ScoutHierarchy.objects.all(),
        label=_("Pfadfindergruppe"),
        help_text=_("Die Pfadfindergruppe, für die du anmeldest"),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        event = kwargs.pop("event", None)
        event_module = kwargs.pop("event_module", None)
        super().__init__(*args, **kwargs)

        if event:
            # Modify fields based on event registration_type
            if event.registration_type:
                # Configure scout_group field based on registration_type settings
                if event.registration_type.need_scout_group:
                    self.fields["scout_group"].required = True

                    # If registration specifies a level, filter available groups
                    level_filter = event.registration_type.level_choice
                    if level_filter:
                        self.fields["scout_group"].queryset = (
                            ScoutHierarchy.objects.filter(level_choice=level_filter)
                        )
                else:
                    # If scout group not needed, remove the field
                    del self.fields["scout_group"]

            # Add additional custom fields specific to this event if needed


class RegistrationListFilter(forms.Form):
    """
    Filter form for EventListView
    """

    query = forms.CharField(
        required=False,
        label=_("Suche"),
        widget=forms.TextInput(
            attrs={"placeholder": _("Suche nach Name, Pfadfindername oder Gruppe")}
        ),
    )
    event = forms.ModelChoiceField(
        queryset=Event.objects.filter(is_public=True),
        label=_("Veranstaltung"),
        required=False,
        help_text=_("Die Veranstaltung, für die du anmeldest"),
        widget=forms.Select(
            attrs={
                "class": "shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md"
            }
        ),
    )


class RegistrationBaseForm(forms.ModelForm):
    """
    Base form for all registration forms.
    """

    class Meta:
        model = Registration
        fields = ["scout_organisation", "responsible_persons"]


# class ParticipantForm(forms.Form):
#     """
#     Form for RegistrationParticipant
#     """

#     scout_name = forms.CharField(
#         required=False,
#         label=_("Pfadfindername"),
#         help_text=_("Fahrtenname oder Spitzname der Person"),
#     )
#     first_name = forms.CharField(
#         required=True,
#         label=_("Vorname"),
#         help_text=_("Vorname der Person oder mehrere Vornamen"),
#     )
#     last_name = forms.CharField(
#         required=True,
#         label=_("Nachname"),
#         help_text=_("Nachname der Person"),
#     )
#     address = forms.CharField(
#         required=True,
#         label=_("Adresse"),
#         help_text=_("Die vollständige Anschrift. z.B. Straße, Hausnummer"),
#     )
#     zip_code = forms.CharField(
#         label=_("PLZ"),
#         max_length=10,
#         required=False,
#         widget=HtmxAutocompleteWidget(
#             url="/master-data/zip-code-autocomplete",
#             min_chars=2,
#             attrs={"class": "tailwind-input", "placeholder": _("PLZ eingeben")},
#         ),
#     )
#     scout_group = forms.ModelChoiceField(
#         required=False,
#         queryset=ScoutHierarchy.objects.all(),
#         label=_("Pfadfindergruppe"),
#         help_text=_("Die Pfadfindergruppe, zu der die Person gehört"),
#     )
#     birthday = forms.DateField(
#         required=True,
#         label=_("Geburtsdatum"),
#         help_text=_("Das Geburtsdatum im Format TT.MM.JJJJ"),
#     )
#     booking_option = forms.ModelChoiceField(
#         required=True,
#         queryset=BookingOption.objects.none(),
#         label=_("Buchungsoption"),
#         help_text=_("Die gewählte Teilnahmeoption für die Veranstaltung"),
#     )
#     gender = forms.ChoiceField(
#         required=True,
#         choices=event_choices.Gender.choices,
#         label=_("Geschlecht"),
#         help_text=_("Das Geschlecht der Person"),
#     )
#     eat_habit = forms.ModelMultipleChoiceField(
#         required=False,
#         queryset=NutritionalTag.objects.all(),
#         label=_("Essgewohnheiten"),
#         help_text=_("Die Essgewohnheiten der Person"),
#         widget=forms.CheckboxSelectMultiple(),
#     )

#     def __init__(self, *args, **kwargs):
#         registration_id = kwargs.pop("registration_id", None)
#         event_module = kwargs.pop("event_module", None)
#         event = kwargs.pop("event", None)
#         super(ParticipantForm, self).__init__(*args, **kwargs)

#         if event:
#             # Filter booking options by the event associated with the registration
#             self.fields["booking_option"].queryset = BookingOption.objects.filter(
#                 event=event
#             )
#             self.fields["booking_option"].initial = BookingOption.objects.filter(
#                 event=event
#             ).first()


class DynamicModuleForm(forms.Form):
    """
    Dynamic form for event modules that includes all connected attribute modules
    """

    def __init__(self, *args, **kwargs):
        event_module = kwargs.pop("event_module", None)
        event = kwargs.pop("event", None)
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
                if attribute_module.field_type == "InA":
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
                elif attribute_module.field_type == "DaA":
                    self.fields[field_name] = forms.DateField(
                        label=field_label,
                        required=attribute_module.is_required,
                        widget=forms.DateInput(attrs={"type": "date"}),
                        help_text=attribute_module.text,
                    )
                elif attribute_module.field_type == "FlA":
                    self.fields[field_name] = forms.FloatField(
                        label=field_label,
                        required=attribute_module.is_required,
                        widget=forms.NumberInput(attrs={"step": "any"}),
                        help_text=attribute_module.text,
                    )
                elif attribute_module.field_type == "StA":
                    self.fields[field_name] = forms.CharField(
                        label=field_label,
                        required=attribute_module.is_required,
                        widget=forms.TextInput(),
                        help_text=attribute_module.text,
                    )
                elif attribute_module.field_type == "HtA":
                    self.fields[field_name] = forms.CharField(
                        label=field_label,
                        required=attribute_module.is_required,
                        widget=forms.Textarea(attrs={"class": "html-editor"}),
                        help_text=attribute_module.text,
                    )
                elif attribute_module.field_type == "RaA":
                    # Get choice options from the database instead of parsing text
                    choices = []
                    choice_options = AttributeChoiceOption.objects.filter(attribute_module=attribute_module)
                    if choice_options.exists():
                        choices = [(option.id, option.text) for option in choice_options]
                    else:
                        # Fallback to parsing text if no options in database
                        choices = []
                    
                    self.fields[field_name] = forms.ChoiceField(
                        label=field_label,
                        required=attribute_module.is_required,
                        widget=forms.RadioSelect(),
                        choices=choices,
                        help_text=attribute_module.text,
                    )
                elif attribute_module.field_type == "MuA":
                    choices = []
                    choice_options = AttributeChoiceOption.objects.filter(attribute_module=attribute_module)
                    if choice_options.exists():
                        choices = [(option.id, option.text) for option in choice_options]
                    else:
                        # Fallback to parsing text if no options in database
                        choices = []
                    self.fields[field_name] = forms.MultipleChoiceField(
                        choices=choices,
                        label=field_label,
                        required=attribute_module.is_required,
                        widget=forms.CheckboxSelectMultiple(),
                        help_text=attribute_module.text,
                    )
                elif attribute_module.field_type == "ZiA":
                    self.fields[field_name] = forms.CharField(
                        label=field_label,
                        required=attribute_module.is_required,
                        widget=HtmxAutocompleteWidget(
                            url="/master-data/zip-code-autocomplete",
                            min_chars=2,
                            attrs={
                                "class": "tailwind-input",
                                "placeholder": _("PLZ eingeben"),
                            },
                        ),
                        help_text=attribute_module.text,
                    )
                elif attribute_module.field_type == "EmA":
                    self.fields[field_name] = forms.EmailField(
                        label=field_label,
                        required=attribute_module.is_required,
                        widget=forms.EmailInput(
                            attrs={"placeholder": "email@example.com"}
                        ),
                        help_text=attribute_module.text,
                    )
                elif attribute_module.field_type == "PhA":
                    self.fields[field_name] = forms.CharField(
                        label=field_label,
                        required=attribute_module.is_required,
                        widget=forms.TextInput(
                            attrs={"placeholder": "+49 123 4567890"}
                        ),
                        help_text=attribute_module.text,
                    )
                elif attribute_module.field_type == "ScA":
                    self.fields[field_name] = forms.ModelChoiceField(
                        label=field_label,
                        required=attribute_module.is_required,
                        queryset=ScoutHierarchy.objects.all(),
                        help_text=attribute_module.text,
                    )


def create_module_form_class(event_module):
    """
    Factory function to create a form class for a specific event module
    """
    class_name = f"EventModule{event_module.id}Form"
    return type(class_name, (DynamicModuleForm,), {})


class ParticipantSearchForm(forms.Form):
    """
    Form for searching participants
    """

    search = forms.CharField(
        required=False,
        label=_("Suche"),
        widget=forms.TextInput(attrs={"placeholder": _("Name oder Pfadfindername")}),
    )
    scout_group = forms.ModelChoiceField(
        queryset=ScoutHierarchy.objects.all(),
        label=_("Pfadfindergruppe"),
        required=False,
    )
    booking_option = forms.ModelChoiceField(
        queryset=BookingOption.objects.none(),
        label=_("Buchungsoption"),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        event = kwargs.pop("event", None)
        reg = kwargs.pop("reg", None)
        super().__init__(*args, **kwargs)

        if event:
            self.fields["booking_option"].queryset = BookingOption.objects.filter(
                event=event
            )

            if event.registration_type and event.registration_type.level_choice:
                self.fields["scout_group"].queryset = ScoutHierarchy.objects.filter(
                    level_choice=event.registration_type.level_choice
                )


class PrivacySearchForm(forms.Form):
    """
    Form for searching participants
    """

    search = forms.CharField(
        required=False,
        label=_("Suche"),
        widget=forms.TextInput(attrs={"placeholder": _("Name oder Pfadfindername")}),
    )
    scout_group = forms.ModelChoiceField(
        queryset=ScoutHierarchy.objects.all(),
        label=_("Pfadfindergruppe"),
        required=False,
    )


class RegistrationRevocationForm(forms.Form):
    """
    Form to confirm the revocation of a registration.
    """

    confirm = forms.BooleanField(
        required=True,
        label=_("Bestätigung"),
        help_text=_(
            "Ich verstehe, dass diese Aktion nicht rückgängig gemacht werden kann."
        ),
        widget=forms.CheckboxInput(
            attrs={"class": "form-checkbox h-5 w-5 text-blue-600"}
        ),
    )
    reason = forms.ChoiceField(
        required=False,
        label=_("Begründung"),
        help_text=_("Bitte wähle einen Grund für die Löschung der Anmeldung aus."),
        choices=[("", "------")] + list(DELETION_REASONS),
        widget=forms.Select(
            attrs={
                "class": "shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md"
            }
        ),
    )
