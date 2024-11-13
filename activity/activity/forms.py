from django import forms
from django.forms.models import inlineformset_factory, formset_factory
from django.core.validators import MinValueValidator, MaxValueValidator
from ckeditor.widgets import CKEditorWidget
from image_cropping import ImageCropWidget

from . import choices as activity_choices

from .choices import (
    ExecutionTimeChoices,
    DifficultyChoices,
    CostsRatingChoices,
    PrepairationTimeChoices,
    StatusChoices,
    StatusSearchChoices
)
from .models import (
    MaterialUnit,
    Activity,
    Topic,
    MaterialItem,
    ScoutLevelChoice,
    ActivityTypeChoice,
    LocationChoice,
    TimeChoice,
)

from general.login.models import CustomUser


class ActivityForm(forms.ModelForm):
    title = forms.CharField(
        label="Titel der Aktivität",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        help_text="Das ist der Haupttitel der Aktivität",
    )
    overview = forms.CharField(
        label="Zusammenfassung",
        widget=forms.Textarea,
        required=True,
        help_text="Die Zusammenfassung wird auf der Startseite angezeigt",
    )
    content = forms.CharField(
        label="Inhalt der Aktivität",
        widget=CKEditorWidget(attrs={"class": "col-span-2"}),
        required=True,
        help_text="Der Inhalt der Aktivität",
    )

    class Meta:
        model = Activity
        fields = [
            "title",
            "overview",
            "content",
        ]


class ActivityUpdateForm(forms.ModelForm):
    title = forms.CharField(
        label="Titel der Aktivität",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        help_text="Das ist der Haupttitel der Aktivität",
    )
    overview = forms.CharField(
        label="Zusammenfassung",
        widget=forms.Textarea,
        required=True,
        help_text="Die Zusammenfassung wird auf der Startseite angezeigt",
    )
    content = forms.CharField(
        label="Inhalt der Aktivität",
        widget=CKEditorWidget(attrs={"class": "col-span-2"}),
        required=True,
        help_text="Der Inhalt der Aktivität",
    )

    class Meta:
        model = Activity
        fields = [
            "title",
            "overview",
            "content",
        ]


class SearchForm(forms.Form):

    query = forms.CharField(
        label="Suche",
        max_length=100,
        required=False,
        widget=forms.HiddenInput(),
    )

    status = forms.ChoiceField(
        choices=activity_choices.StatusSearchChoices,
        widget=forms.RadioSelect(
            attrs={"class": "tailwind-radio", "onchange": "submit();"}
        ),
        required=True,
    )


class CommentForm(forms.Form):
    content = forms.CharField(label="Content", widget=forms.Textarea)
    post = forms.IntegerField(widget=forms.HiddenInput())
    author = forms.IntegerField(widget=forms.HiddenInput())


class IntroForm(forms.Form):
    agreement = forms.BooleanField(
        label="Ich habe verstanden",
        required=True,
    )


class MainTextForm(forms.ModelForm):
    description = forms.CharField(
        label="Inhalt des Artikels",
        widget=CKEditorWidget(attrs={"class": "col-span-2"}),
        required=True,
        help_text="Der Inhalt des Artikels",
    )

    class Meta:
        model = Activity
        fields = [
            "description",
        ]


class HeaderTextForm(forms.ModelForm):
    title = forms.CharField(
        label="Titel deiner Idee",
        widget=forms.TextInput(attrs={"class": "tailwind-input"}),
        required=True,
        help_text="Formuliere den Titel deiner Idee",
    )
    summary = forms.CharField(
        label="Zusammenfassung",
        widget=forms.Textarea(attrs={"class": "tailwind-textarea"}),
        required=True,
        help_text="Die Zusammenfassung wird auf der Startseite angezeigt",
    )

    class Meta:
        model = Activity
        fields = [
            "title",
            "summary",
        ]


class RatingForm(forms.ModelForm):
    costs_rating = forms.ChoiceField(
        choices=CostsRatingChoices.choices,
        widget=forms.RadioSelect,
        required=True,
        label="Kosten",
    )
    difficulty = forms.ChoiceField(
        choices=DifficultyChoices.choices,
        widget=forms.RadioSelect,
        required=True,
        label="Schwierigkeit",
    )
    execution_time = forms.ChoiceField(
        choices=ExecutionTimeChoices.choices,
        widget=forms.RadioSelect,
        required=True,
        label="Dauer",
    )
    preparation_time = forms.ChoiceField(
        choices=PrepairationTimeChoices.choices,
        widget=forms.RadioSelect,
        required=True,
        label="Vorbereitungszeit",
    )

    class Meta:
        model = Activity
        fields = [
            "costs_rating",
            "difficulty",
            "execution_time",
            "preparation_time",
        ]


class TopicForm(forms.ModelForm):
    topics = forms.ModelMultipleChoiceField(
        queryset=Topic.objects.all(),
        required=True,
        label="Themen",
        widget=forms.CheckboxSelectMultiple(
            attrs={"class": "tailwind-checkbox"}
        ),
        help_text="",
    )

    class Meta:
        model = Activity
        fields = [
            "topics",
        ]


class ChoicesForm(forms.ModelForm):
    scout_levels = forms.ModelMultipleChoiceField(
        queryset=ScoutLevelChoice.objects.all(),
        required=True,
        # max 3 choices
        label="Für welche Altersgruppe ist die Idee geeignet?",
        widget=forms.CheckboxSelectMultiple(
            attrs={"class": "tailwind-checkbox"}
        ),
        help_text=""
    )
    activity_types = forms.ModelMultipleChoiceField(
        queryset=ActivityTypeChoice.objects.all(),
        required=True,
        label="Welche Art von Aktivität ist es?",
        widget=forms.CheckboxSelectMultiple(
            attrs={"class": "tailwind-checkbox"}
        ),
        help_text="",
    )
    locations = forms.ModelMultipleChoiceField(
        queryset=LocationChoice.objects.all(),
        required=True,
        label="Wo kann die Idee umgesetzt werden?",
        widget=forms.CheckboxSelectMultiple(
            attrs={"class": "tailwind-checkbox"}
        ),
        help_text="",
    )
    times = forms.ModelMultipleChoiceField(
        queryset=TimeChoice.objects.all(),
        required=True,
        label="Wann kann die Idee umgesetzt werden?",
        widget=forms.CheckboxSelectMultiple(
            attrs={"class": "tailwind-checkbox"}
        ),
        help_text="",
    )

    class Meta:
        model = Activity
        fields = [
            "scout_levels",
            "activity_types",
            "locations",
            "times",
        ]


class ImageForm(forms.ModelForm):
    image = forms.ImageField(
        label="Bild",
        required=False,
        widget=ImageCropWidget,
        help_text="Füge ein Bild hinzu",
    )

    class Meta:
        model = Activity
        fields = [
            "image",
            "cropping",

        ]


class UnkownForm(forms.Form):
    created_by_email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"class": "form-control"}),
        required=True,
        help_text="Deine Email",
    )
    created_by_name = forms.CharField(
        label="Name",
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=True,
        help_text="Dein Name",
    )
    status = forms.ChoiceField(
        choices=StatusChoices.choices,
        widget=forms.RadioSelect(attrs={"class": "form-control"}),
        required=True,
        label="Status",
        help_text="Wähle den Status deiner Idee.",
    )

class CreatorForm(forms.ModelForm):
    status= forms.ChoiceField(
        choices=StatusChoices.choices,
        widget=forms.RadioSelect(attrs={"class": "form-control"}),
        required=True,
        label="Status",
        help_text="Wähle den Status deiner Idee.",
    )
    authors = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.all(),
        required=False,
        label="Autoren",
        help_text="Wähle die Autoren deiner Idee",
    )

    class Meta:
        model = Activity
        fields = [
            "status",
            "authors",
        ]

class StatusSearchFrom(forms.Form):
    query = forms.CharField(
        label="Suche",
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Suche nach ...",
            }
        ),
    )
    status = forms.ChoiceField(
        choices=StatusSearchChoices.choices,
        widget=forms.RadioSelect(attrs={"class": "form-control"}),
        label="Status",
        required=False,
    )
    


class MaterialItemForm(forms.Form):
    material_name = forms.CharField(
        label="Material",
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=True,
    )
    material_unit = forms.ModelChoiceField(
        queryset=MaterialUnit.objects.all(),
        required=True,
        label="Einheit",
    )
    quantity = forms.FloatField(
        label="Menge für 6 Personen",
        validators=[MinValueValidator(0), MaxValueValidator(1000)],
        required=True,
    )


class MaterialItemModelForm(forms.ModelForm):
    material_name = forms.CharField(
        label="Material",
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=True,
    )
    material_unit = forms.ModelChoiceField(
        queryset=MaterialUnit.objects.all(),
        required=True,
        label="Einheit",
    )
    quantity = forms.FloatField(
        label="Menge",
        validators=[MinValueValidator(0), MaxValueValidator(1000)],
        required=True,
    )

    class Meta:
        model = MaterialItem
        fields = [
            "material_name",
            "material_unit",
            "quantity",
        ]


class MaterialForm(forms.Form):
    pass