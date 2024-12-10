from django import forms
from ckeditor.widgets import CKEditorWidget

from .choices import StatusType, StatusTypeWithAll
from .models import Category, Post
from general.login.models import CustomUser


class PostForm(forms.ModelForm):
    title = forms.CharField(
        label="Titel des Artikels",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        help_text="Das ist der Haupttitel des Artikels",
    )
    overview = forms.CharField(
        label="Zusammenfassung",
        widget=forms.Textarea,
        required=True,
        help_text="Die Zusammenfassung wird auf der Startseite angezeigt",
    )
    content = forms.CharField(
        label="Inhalt des Artikels",
        widget=CKEditorWidget(attrs={"class": "col-span-2"}),
        required=True,
        help_text="Der Inhalt des Artikels",
    )
    thumbnail = forms.ImageField(
        required=False,
        label="Hauptbild",
        help_text="Bild, das auf der Startseite angezeigt wird",
    )

    class Meta:
        model = Post
        fields = [
            "title",
            "overview",
            "content",
            "thumbnail",
            "categories",
        ]

class PostFormUpdate(forms.ModelForm):
    title = forms.CharField(
        label="Titel des Artikels",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        help_text="Das ist der Haupttitel des Artikels",
    )
    overview = forms.CharField(
        label="Zusammenfassung",
        widget=forms.Textarea,
        required=True,
        help_text="Die Zusammenfassung wird auf der Startseite angezeigt",
    )
    content = forms.CharField(
        label="Inhalt des Artikels",
        widget=CKEditorWidget(attrs={"class": "col-span-2"}),
        required=True,
        help_text="Der Inhalt des Artikels",
    )
    thumbnail = forms.ImageField(
        required=False,
        label="Hauptbild",
        help_text="Bild, das auf der Startseite angezeigt wird",
    )
    # author = forms.Select(
    #     choices=[(user.id, user.username) for user in CustomUser.objects.all()],
    # )
    status = forms.ChoiceField(
        choices=StatusType,
        initial="all",
        widget=forms.RadioSelect(attrs={"class": "tailwind-radio"}),
        required=True,
    )

    class Meta:
        model = Post
        fields = [
            "title",
            "overview",
            "content",
            "thumbnail",
            "categories",
            "author",
            "status",
        ]


class SearchForm(forms.Form):

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

    # with additional class 'form-control' for bootstrap
    status = forms.ChoiceField(
        choices=StatusTypeWithAll,
        required=False,
        widget=forms.RadioSelect(
            attrs={"class": "tailwind-radio", "onchange": "submit();"}
        ),
    )

class CommentForm(forms.Form):
    content = forms.CharField(label="Content", widget=forms.Textarea)
    post = forms.IntegerField(widget=forms.HiddenInput())
    author = forms.IntegerField(widget=forms.HiddenInput())
    status = forms.ChoiceField(widget=forms.HiddenInput(), choices=StatusType)
