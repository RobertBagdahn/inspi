from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .models import Event, EventLocation
from .models import EventPermission
from django.forms import formset_factory, BaseFormSet
from django.contrib.auth import get_user_model
from group.models import InspiGroup
from general.login.models import CustomUser
from .models import EventPermissionType, BookingOption, EventModule


class EventListFilter(forms.Form):
    """
    Filter form for EventListView
    """

    name = forms.CharField(
        label=_("Name"),
        required=False,
        widget=forms.TextInput(attrs={"placeholder": _("Nach Namen suchen")}),
    )

    start_date = forms.DateField(
        label=_("Startdatum"),
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    end_date = forms.DateField(
        label=_("Enddatum"),
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    active = forms.BooleanField(
        label=_("Nur aktive Veranstaltungen"), required=False, initial=True
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
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": _("Gruppennamen eingeben")}),
        label=_("Name deiner Gruppe"),
    )

    class Meta:
        model = Event
        fields = [
            "name",
        ]


class EventIntroForm(forms.Form):
    """Introduction step for the event creation wizard."""

    xxx = forms.CharField(
        label=_("Einleitung"),
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": "tailwind-input"}),
        help_text=_("Gib eine kurze Einleitung zur Veranstaltung ein"),
    )


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
        required=True,
        widget=forms.Select(attrs={"class": "tailwind-input"}),
        help_text=_("Wähle einen vorhandenen Veranstaltungsort aus"),
    )


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


class BookingOptionForm(forms.ModelForm):
    """Form for creating and updating booking options."""

    name = forms.CharField(
        label=_("Name der Buchungsoption"),
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={"class": "tailwind-input"}),
        help_text=_("Gib den Namen für diese Buchungsoption ein"),
    )

    description = forms.CharField(
        label=_("Beschreibung"),
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": "tailwind-input"}),
        help_text=_("Beschreibe diese Buchungsoption"),
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
            attrs={"type": "datetime-local", "class": "tailwind-input"}
        ),
        help_text=_("Ab wann die Option buchbar ist"),
    )

    bookable_till = forms.DateTimeField(
        label=_("Buchbar bis"),
        required=False,
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local", "class": "tailwind-input"}
        ),
        help_text=_("Bis wann die Option buchbar ist"),
    )

    start_date = forms.DateTimeField(
        label=_("Startdatum"),
        required=False,
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local", "class": "tailwind-input"}
        ),
        help_text=_("Wann die Option beginnt"),
    )

    end_date = forms.DateTimeField(
        label=_("Enddatum"),
        required=False,
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local", "class": "tailwind-input"}
        ),
        help_text=_("Wann die Option endet"),
    )

    class Meta:
        model = BookingOption
        fields = [
            "name",
            "description",
            "price",
            "max_participants",
            "bookable_from",
            "bookable_till",
            "start_date",
            "end_date",
        ]


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
