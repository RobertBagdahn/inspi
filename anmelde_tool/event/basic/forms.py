from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .models import Event
from .models import EventPermission
from django.forms import formset_factory, BaseFormSet
from django.contrib.auth import get_user_model
from group.models import InspiGroup
from general.login.models import CustomUser
from .models import EventPermissionType, BookingOption, EventModule, EventRegistrationType
from masterdata.models import ZipCode, EventLocation
from masterdata.widgets import HtmxAutocompleteWidget


class EventListFilter(forms.Form):
    """
    Filter form for EventListView
    """

    name = forms.CharField(
        label='Suche',
        required=False,
        widget=forms.TextInput(attrs={"placeholder": _("Nach Namen suchen")}),
    )
    is_future = forms.BooleanField(
        label=_("Nur zukünftige Veranstaltungen"), required=False, initial=True
    )

    def filter_queryset(self, queryset):
        """
        Filter the provided queryset based on form data
        """
        if self.is_valid():
            data = self.cleaned_data

            if data.get("name"):
                queryset = queryset.filter(name__icontains=data["name"])

            if data.get("start_date"):
                queryset = queryset.filter(start_date__gte=data["start_date"])

            if data.get("end_date"):
                queryset = queryset.filter(end_date__lte=data["end_date"])

            if data.get("active"):
                queryset = queryset.filter(is_active=True)

        return queryset


class EventCreateForm(forms.ModelForm):
    """Form for creating events."""

    name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            attrs={"placeholder": _("Veranstaltungsnamen eingeben")}
        ),
        label=_("Name der Veranstaltung"),
    )

    slug = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": _("Kurz-URL eingeben")}),
        label=_("Kurz-URL"),
        help_text=_("Einzigartiger Bezeichner für die URL der Veranstaltung"),
    )

    short_description = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": _("Kurze Beschreibung eingeben")}),
        label=_("Kurzbeschreibung"),
    )

    long_description = forms.CharField(
        max_length=10000,
        required=False,
        widget=forms.Textarea(
            attrs={"rows": 5, "placeholder": _("Ausführliche Beschreibung eingeben")}
        ),
        label=_("Ausführliche Beschreibung"),
    )

    location = forms.ModelChoiceField(
        queryset=EventLocation.objects.all(),
        required=False,
        label=_("Veranstaltungsort"),
    )

    registration_type = forms.ModelChoiceField(
        queryset=EventRegistrationType.objects.all(),
        required=False,
        label=_("Anmeldetyp"),
        help_text=_("Wählen Sie den Anmeldetyp für die Veranstaltung aus"),
    )

    start_date = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
        ),
        label=_("Startdatum"),
    )

    end_date = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
        ),
        label=_("Enddatum"),
    )

    registration_start = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
        ),
        label=_("Anmeldebeginn"),
    )

    registration_deadline = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
        ),
        label=_("Anmeldefrist"),
    )

    last_possible_update = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
        ),
        label=_("Letzte Änderungsmöglichkeit"),
    )

    is_public = forms.BooleanField(
        required=False,
        initial=False,
        label=_("Öffentliche Veranstaltung"),
        help_text=_("Aktivieren, um die Veranstaltung öffentlich sichtbar zu machen"),
    )

    class Meta:
        model = Event
        fields = [
            "name",
            "slug",
            "short_description",
            "long_description",
            "is_public",
            "location",
            "registration_type",
            "start_date",
            "end_date",
            "registration_start",
            "registration_deadline",
            "last_possible_update",
            "is_public",
        ]


class EventIntroForm(forms.Form):
    """Introduction step for the event creation wizard."""

    # xxx = forms.CharField(
    #     label=_("Einleitung"),
    #     max_length=100,
    #     required=False,
    #     widget=forms.TextInput(attrs={"class": "tailwind-input"}),
    #     help_text=_("Gib eine kurze Einleitung zur Veranstaltung ein"),
    # )


class EventBasicInfoForm(forms.Form):
    """Basic information step for the event creation wizard."""

    name = forms.CharField(
        label=_("Veranstaltungsname"),
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"class": "tailwind-input"}),
        help_text=_("Gib den Namen der Veranstaltung ein"),
    )
    short_description = forms.CharField(
        label=_("Kurzbeschreibung"),
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": "tailwind-input"}),
        help_text=_("Gib eine kurze Beschreibung der Veranstaltung ein"),
    )

    long_description = forms.CharField(
        label=_("Ausführliche Beschreibung"),
        max_length=10000,
        required=False,
        widget=forms.Textarea(attrs={"class": "tailwind-input", "rows": 5}),
        help_text=_("Gib eine detaillierte Beschreibung der Veranstaltung ein"),
    )


class EventLocationForm(forms.Form):
    """Location step for the event creation wizard."""

    # If you have a Location model, you could use a ModelChoiceField instead
    location = forms.ModelChoiceField(
        label=_("Veranstaltungsort"),
        queryset=EventLocation.objects.all(),
        required=False,
        widget=forms.Select(attrs={"class": "tailwind-input"}),
        help_text=_("Wähle einen vorhandenen Veranstaltungsort aus"),
    )
    add_new_location = forms.BooleanField(
        label=_("Neuen Veranstaltungsort hinzufügen"),
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "tailwind-checkbox"}),
        help_text=_(
            "Aktiviere dieses Feld, um einen neuen Veranstaltungsort hinzuzufügen"
        ),
    )

    def clean(self):
        cleaned_data = super().clean()
        location = cleaned_data.get("location")
        add_new_location = cleaned_data.get("add_new_location")

        if location and add_new_location:
            raise forms.ValidationError(
                _(
                    "Entweder einen vorhandenen Veranstaltungsort auswählen oder einen neuen erstellen."
                )
            )

        # Check that either a location is selected or add_new_location is true
        if not location and not add_new_location:
            raise forms.ValidationError(
                _(
                    "Bitte wähle entweder einen vorhandenen Veranstaltungsort aus oder erstelle einen neuen."
                )
            )

        return cleaned_data


class EventLocationCreationForm(forms.Form):
    """Form for creating a new event location."""

    name = forms.CharField(
        label=_("Name des Veranstaltungsortes"),
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"class": "tailwind-input"}),
        help_text=_("Gib den Namen des neuen Veranstaltungsortes ein"),
    )

    street = forms.CharField(
        label=_("Straße"),
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": "tailwind-input"}),
        help_text=_("Straße und Hausnummer"),
    )

    zip_code = forms.CharField(
        label=_("PLZ113"),
        max_length=10,
        required=False,
        widget=HtmxAutocompleteWidget(
            url="/master-data/zip-code-autocomplete",
            min_chars=2,
            attrs={"class": "tailwind-input", "placeholder": _("PLZ eingeben")}
        ),
    )

    def clean(self):
        cleaned_data = super().clean()
        zip_code = cleaned_data.get("zip_code")

        # If zip_code is provided, you can add validation logic here
        if zip_code:
            # Example: Check if zip_code is numeric
            if not zip_code.isdigit():
                self.add_error(
                    "zip_code", _("Die Postleitzahl darf nur Zahlen enthalten.")
                )

            # Example: Check length for German zip codes
            if len(zip_code) != 5:
                self.add_error(
                    "zip_code", _("Die Postleitzahl muss aus 5 Ziffern bestehen.")
                )

            # Check if zip_code exists in the master data
            if not ZipCode.objects.filter(zip_code=zip_code).exists():
                self.add_error(
                    "zip_code", _("Die angegebene Postleitzahl ist nicht gültig.")
                )

        return cleaned_data


class EventScheduleForm(forms.Form):
    """Schedule step for the event creation wizard."""

    start_date = forms.DateTimeField(
        label=_("Startdatum"),
        required=True,
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local", "class": "tailwind-input"}
        ),
        help_text=_("Wähle Datum und Uhrzeit für den Beginn der Veranstaltung"),
    )
    end_date = forms.DateTimeField(
        label=_("Enddatum"),
        required=True,
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local", "class": "tailwind-input"}
        ),
        help_text=_("Wähle Datum und Uhrzeit für das Ende der Veranstaltung"),
    )
    registration_start = forms.DateTimeField(
        label=_("Anmeldebeginn"),
        required=False,
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local", "class": "tailwind-input"}
        ),
        help_text=_(
            "Zeitpunkt, ab dem die Anmeldung für die Veranstaltung möglich ist"
        ),
    )
    registration_deadline = forms.DateTimeField(
        label=_("Anmeldefrist"),
        required=False,
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local", "class": "tailwind-input"}
        ),
        help_text=_("Letzter Tag für die Anmeldung zur Veranstaltung"),
    )
    last_possible_update = forms.DateTimeField(
        label=_("Letzte Änderungsmöglichkeit"),
        required=False,
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local", "class": "tailwind-input"}
        ),
        help_text=_("Letztes Datum, an dem Teilnehmer ihre Anmeldung ändern können"),
    )


class EventPermissionForm(forms.Form):
    """Invitation step for the event creation wizard."""

    user = forms.ModelChoiceField(
        queryset=CustomUser.objects.all(),
        required=False,
        label=_("Benutzer"),
        widget=forms.Select(attrs={"class": "tailwind-input"}),
    )

    group = forms.ModelChoiceField(
        queryset=InspiGroup.objects.all(),
        required=False,
        label=_("Gruppe"),
        widget=forms.Select(attrs={"class": "tailwind-input"}),
    )

    permission_type = forms.ChoiceField(
        choices=EventPermissionType.choices,
        initial=EventPermissionType.VIEW,
        widget=forms.Select(attrs={"class": "tailwind-input"}),
        label=_("Berechtigungstyp"),
    )

    include_subgroups = forms.BooleanField(
        label=_("Untergruppen einbeziehen"),
        initial=False,
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "tailwind-checkbox"}),
        help_text=_(
            "Falls aktiviert, erhalten auch alle Untergruppen diese Berechtigung"
        ),
    )

    class Meta:
        model = EventPermission
        fields = ["user", "group", "permission_type", "include_subgroups"]

    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get("user")
        group = cleaned_data.get("group")

        if not user and not group:
            raise forms.ValidationError(
                _("Entweder ein Benutzer oder eine Gruppe muss angegeben werden")
            )
        if user and group:
            raise forms.ValidationError(
                _(
                    "Es kann nicht gleichzeitig ein Benutzer und eine Gruppe angegeben werden"
                )
            )

        return cleaned_data


class EventPermissionCreateForm(forms.ModelForm):
    """Invitation step for the event creation wizard."""

    user = forms.ModelChoiceField(
        queryset=CustomUser.objects.all(),
        required=False,
        label=_("Benutzer"),
        widget=forms.Select(attrs={"class": "tailwind-input"}),
    )

    group = forms.ModelChoiceField(
        queryset=InspiGroup.objects.all(),
        required=False,
        label=_("Gruppe"),
        widget=forms.Select(attrs={"class": "tailwind-input"}),
    )

    permission_type = forms.ChoiceField(
        choices=EventPermissionType.choices,
        initial=EventPermissionType.VIEW,
        widget=forms.Select(attrs={"class": "tailwind-input"}),
        label=_("Berechtigungstyp"),
    )

    include_subgroups = forms.BooleanField(
        label=_("Untergruppen einbeziehen"),
        initial=False,
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "tailwind-checkbox"}),
        help_text=_(
            "Falls aktiviert, erhalten auch alle Untergruppen diese Berechtigung"
        ),
    )

    class Meta:
        model = EventPermission
        fields = ["user", "group", "permission_type", "include_subgroups"]

    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get("user")
        group = cleaned_data.get("group")

        if not user and not group:
            raise forms.ValidationError(
                _("Entweder ein Benutzer oder eine Gruppe muss angegeben werden")
            )
        if user and group:
            raise forms.ValidationError(
                _(
                    "Es kann nicht gleichzeitig ein Benutzer und eine Gruppe angegeben werden"
                )
            )

        return cleaned_data


class BaseEventPermissionFormSet(BaseFormSet):
    """Base formset for managing multiple event permission forms."""

    def clean(self):
        if any(self.errors):
            print("Errors in formset, skipping validation")
            return

        for form in self.forms:
            if not form.cleaned_data:
                continue


EventPermissionFormSet = formset_factory(
    EventPermissionForm, formset=BaseEventPermissionFormSet, extra=1, can_delete=True
)


class EventSummaryForm(forms.Form):
    checkbox = forms.BooleanField(
        label=_(
            "Ich habe alle Informationen überprüft und bin bereit, die Veranstaltung zu erstellen."
        ),
        required=True,
        widget=forms.CheckboxInput(attrs={"class": "tailwind-checkbox"}),
    )


class BookingOptionForm(forms.Form):
    """Form for creating and updating booking options."""

    name = forms.CharField(
        label=_("Name der Buchungsoption"),
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={"class": "tailwind-input"}),
        help_text=_("Gib den Namen für diese Buchungsoption ein"),
    )

    description = forms.CharField(
        label=_("Erklärung"),
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": "tailwind-input"}),
        help_text=_("Erkläre diese Buchungsoption"),
    )

    price = forms.DecimalField(
        label=_("Preis"),
        max_digits=5,
        decimal_places=2,
        required=True,
        initial=0.00,
        widget=forms.NumberInput(attrs={"class": "tailwind-input", "step": "0.01"}),
        help_text=_("Preis für diese Option in Euro"),
    )

    max_participants = forms.IntegerField(
        label=_("Maximale Teilnehmer"),
        required=False,
        min_value=0,
        initial=0,
        widget=forms.NumberInput(attrs={"class": "tailwind-input"}),
        help_text=_("Maximale Anzahl an möglichen Teilnehmern (0 = unbegrenzt)"),
    )
    bookable_from = forms.DateTimeField(
        label=_("Buchbar ab"),
        required=False,
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local", "class": "tailwind-input"},
            format="%Y-%m-%dT%H:%M",
        ),
        help_text=_("Ab wann die Option buchbar ist"),
    )

    bookable_till = forms.DateTimeField(
        label=_("Buchbar bis"),
        required=False,
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local", "class": "tailwind-input"},
            format="%Y-%m-%dT%H:%M",
        ),
        help_text=_("Bis wann die Option buchbar ist"),
    )

    start_date = forms.DateTimeField(
        label=_("Startdatum"),
        required=False,
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local", "class": "tailwind-input"},
            format="%Y-%m-%dT%H:%M",
        ),
        help_text=_("Die Veranstaltung beginnt für Personen mit dieser Option zu diesem Zeitpunkt"),
    )

    end_date = forms.DateTimeField(
        label=_("Enddatum"),
        required=False,
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local", "class": "tailwind-input"},
            format="%Y-%m-%dT%H:%M",
        ),
        help_text=_("Wann die Option endet"),
    )
    is_public = forms.BooleanField(
        label=_("Öffentlich"),
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={"class": "tailwind-checkbox"}),
        help_text=_("Aktivieren, um die Buchungsoption öffentlich sichtbar zu machen"),
    )



class EventFormModelForm(forms.ModelForm):
    """Form for creating and updating event form models."""

    header = forms.CharField(
        label=_("Überschrift"),
        max_length=100,
        required=True,
        initial="Default Header",
        widget=forms.TextInput(attrs={"class": "tailwind-input"}),
        help_text=_("Überschrift des Formulars"),
    )

    description = forms.CharField(
        label=_("Beschreibung"),
        required=False,
        widget=forms.Textarea(attrs={"class": "tailwind-input", "rows": 3}),
        help_text=_("Beschreibung des Formulars"),
    )

    ordering = forms.IntegerField(
        label=_("Reihenfolge"),
        required=False,
        initial=999,
        widget=forms.NumberInput(attrs={"class": "tailwind-input"}),
        help_text=_("Reihenfolge des Formulars"),
    )

    class Meta:
        model = EventModule
        fields = [
            "header",
            "description",
            "ordering",
        ]


class EventModuleForm(forms.Form):
    """Modules step for the event creation wizard."""

    # queryset = EventModule.objects.all()
    modules = forms.ModelMultipleChoiceField(
        queryset=EventModule.objects.filter(id__in=[26, 27, 28, 29, 30]),
        required=False,
        label=_("Veranstaltungs-Module"),
        widget=forms.CheckboxSelectMultiple(
            attrs={"class": "tailwind-checkbox"},
        ),
        help_text=_("Wählen Sie die Module aus, die für diese Veranstaltung verwendet werden sollen"),
    )


class EventPermissionForm(forms.ModelForm):
    """Form for creating and updating event permissions."""

    user = forms.ModelChoiceField(
        queryset=CustomUser.objects.all(),
        required=False,
        label=_("Benutzer"),
        widget=forms.Select(attrs={"class": "tailwind-input"}),
        help_text=_("Wähle einen Benutzer für diese Berechtigung aus"),
    )

    group = forms.ModelChoiceField(
        queryset=InspiGroup.objects.all(),
        required=False,
        label=_("Gruppe"),
        widget=forms.Select(attrs={"class": "tailwind-input"}),
        help_text=_("Wähle eine Gruppe für diese Berechtigung aus"),
    )

    permission_type = forms.ChoiceField(
        choices=EventPermissionType.choices,
        initial=EventPermissionType.VIEW,
        widget=forms.Select(attrs={"class": "tailwind-input"}),
        label=_("Berechtigungstyp"),
        help_text=_("Art der Berechtigung für den Benutzer oder die Gruppe"),
    )

    include_subgroups = forms.BooleanField(
        label=_("Untergruppen einbeziehen"),
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "tailwind-checkbox"}),
        help_text=_(
            "Falls aktiviert, erhalten auch alle Untergruppen diese Berechtigung"
        ),
    )

    class Meta:
        model = EventPermission
        fields = ["user", "group", "permission_type", "include_subgroups"]

    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get("user")
        group = cleaned_data.get("group")

        if not user and not group:
            raise forms.ValidationError(
                _("Entweder ein Benutzer oder eine Gruppe muss angegeben werden")
            )
        if user and group:
            raise forms.ValidationError(
                _(
                    "Es kann nicht gleichzeitig ein Benutzer und eine Gruppe angegeben werden"
                )
            )

        return cleaned_data


class EventPermissionFilter(forms.Form):
    """Filter form for event permissions."""
    search = forms.CharField(
        label=_("Suche"),
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": "tailwind-input", "placeholder": _("Benutzer oder Gruppe suchen")}),
        help_text=_("Gib den Namen des Benutzers oder der Gruppe ein"),
    )
    permission_type = forms.ChoiceField(
        choices=[('', '---------')] + list(EventPermissionType.choices),
        initial='',
        widget=forms.Select(attrs={"class": "tailwind-input"}),
        label="Berechtigungstyp",
        help_text=_("Wählen Sie den Berechtigungstyp aus"),
        required=False,
    )


class EventRegistrationTypeForm(forms.Form):
    """Form for selecting the event registration type."""
    event_registration_type = forms.ModelChoiceField(
        queryset=EventRegistrationType.objects.all(),
        required=False,
        label=_("Anmeldetyp"),
        widget=forms.Select(attrs={"class": "tailwind-input"}),
        help_text=_("Wählen Sie den Anmeldetyp für die Veranstaltung aus"),
    )


class EventRegistrationSearchFilterForm(forms.Form):
    """Filter form for searching events."""
    name = forms.CharField(
        label=_("Veranstaltungsname"),
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": "tailwind-input"}),
        help_text=_("Gib den Namen der Veranstaltung ein"),
    )
    start_date = forms.DateTimeField(
        label=_("Startdatum"),
        required=False,
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local", "class": "tailwind-input"}
        ),
        help_text=_("Gib das Startdatum der Veranstaltung ein"),
    )
    is_not_registered = forms.BooleanField(
        label=_("Noch nicht angemeldet"),
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={"class": "tailwind-checkbox"}),
        help_text=_("Nur Veranstaltungen anzeigen, bei denen du noch nicht angemeldet bist"),
    )