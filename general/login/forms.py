from allauth.account.forms import LoginForm, SignupForm
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
from group.models import InspiGroupMembership
from django.forms import ModelForm
from .models import Person
from masterdata.models import ScoutHierarchy, ZipCode
from event.basic import choices as event_basic_choices
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Div, HTML
from django.db.models import Q

try:
    from autocomplete import ModelAutocomplete, AutocompleteWidget

    LEGACY_AUTOCOMPLETE_API = True
except ImportError:
    from autocomplete import HTMXAutoComplete
    from autocomplete.widgets import Autocomplete as AutocompleteWidget

    LEGACY_AUTOCOMPLETE_API = False


if LEGACY_AUTOCOMPLETE_API:
    class ZipCodeAutocomplete(ModelAutocomplete):
        model = ZipCode
        search_attrs = ["zip_code", "city"]
        route_name = "zipcode-autocomplete"

        @classmethod
        def get_label_for_record(cls, record):
            return f"{record.zip_code} {record.city}"


    zipcode_widget = AutocompleteWidget(
        ac_class=ZipCodeAutocomplete,
        options={"placeholder": "Suche nach PLZ oder Ort..."},
    )
else:
    class ZipCodeAutocomplete(HTMXAutoComplete):
        name = "zipcode-autocomplete"

        class Meta:
            model = ZipCode
            item_value = "id"
            item_label = "zip_code"

        def get_items(self, search=None, values=None):
            if search is not None:
                return ZipCode.objects.filter(
                    Q(zip_code__icontains=search) | Q(city__icontains=search)
                ).values("id", "zip_code", "city")

            if values is not None:
                return ZipCode.objects.filter(id__in=values).values("id", "zip_code", "city")

            return []

        def map_items(self, items, selected=None):
            selected_values = set(selected or [])
            return [
                {
                    "label": f"{item['zip_code']} {item['city']}",
                    "value": str(item["id"]),
                    "selected": str(item["id"]) in selected_values,
                }
                for item in items
            ]


    zipcode_widget = AutocompleteWidget(
        use_ac=ZipCodeAutocomplete,
        options={"placeholder": "Suche nach PLZ oder Ort..."},
    )


class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = (
            "email",
            "username",
            "scout_display_name",
        )


class CustomUserChangeForm(forms.ModelForm):

    # username displays the username of the user
    username = forms.CharField(
        max_length=50,
        label="Username (Nicht änderbar)",
        disabled=True,
        required=False,

    )
    
    class Meta:
        model = CustomUser
        fields = (
            "username",
            "email",
            "scout_display_name",
        )


class MyCustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super(MyCustomLoginForm, self).__init__(*args, **kwargs)


class MySignupForm(SignupForm):

    scout_display_name = forms.CharField(
        max_length=50,
        label="Anzeigename",
        help_text="Der Anzeigename wird auf der Plattform angezeigt und kann von deinem Benutzernamen abweichen.",
    )

    def save(self, request):
        user = super(MySignupForm, self).save(request)
        user.scout_display_name = self.cleaned_data["scout_display_name"]
        user.save()
        return user


class InspiGroupAdminSearchFilterForm(forms.ModelForm):
    search = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "Suche nach Gruppen"}),
        required=False,
        label="",
    )

    class Meta:
        model = InspiGroupMembership
        fields = [
            "search",
        ]


class PersonWizardIntroForm(forms.Form):
    """
    Introduction form for the person wizard
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False


class PersonWizardBasicInfoForm(forms.Form):
    """
    Basic information form for the person wizard
    """
    first_name = forms.CharField(
        max_length=100, 
        label="Vorname", 
        required=True,
        help_text="Dein Vorname"
    )
    last_name = forms.CharField(
        max_length=100, 
        label="Nachname", 
        required=True,
        help_text="Dein Nachname"
    )
    scout_name = forms.CharField(
        max_length=100, 
        label="Pfadfindername", 
        required=False,
        help_text="Dein Pfadfindername (falls vorhanden)"
    )
    gender = forms.ChoiceField(
        choices=event_basic_choices.Gender.choices,
        label="Geschlecht",
        required=True,
        help_text="Dein Geschlecht"
    )
    birthday = forms.DateField(
        label="Geburtstag",
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text="Dein Geburtstag"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False


class PersonWizardContactForm(forms.Form):
    """
    Contact information form for the person wizard
    """
    address = forms.CharField(
        max_length=200, 
        label="Adresse", 
        required=False,
        help_text="Deine Straße und Hausnummer"
    )
    address_supplement = forms.CharField(
        max_length=100, 
        label="Adresszusatz", 
        required=False,
        help_text="z.B. Apartment, Gebäude, etc."
    )
    zip_code = forms.ModelChoiceField(
        queryset=ZipCode.objects.all(), 
        label="Postleitzahl",
        required=False,
        help_text="Deine Postleitzahl",
        widget=zipcode_widget
    )
    city = forms.CharField(
        max_length=100, 
        label="Stadt", 
        required=False,
        help_text="Deine Stadt"
    )
    mobile = forms.CharField(
        max_length=50, 
        label="Handynummer", 
        required=False,
        help_text="Deine Handynummer"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False


class PersonWizardPreferencesForm(forms.Form):
    """
    Preferences form for the person wizard
    """
    eat_habits = forms.ChoiceField(
        choices=event_basic_choices.EatHabit.choices,
        label="Essgewohnheiten",
        required=True,
        help_text="Deine Essgewohnheiten"
    )
    scout_group = forms.ModelChoiceField(
        queryset=ScoutHierarchy.objects.all(),
        label="Pfadfindergruppe",
        required=False,
        help_text="Deine Pfadfindergruppe"
    )
    about_me = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        max_length=500,
        label="Über mich",
        required=False,
        help_text="Kurze Beschreibung über dich"
    )
