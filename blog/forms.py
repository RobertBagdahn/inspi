from django import forms

from .choices import StatusType
from .models import Category


class PostForm(forms.Form):
    title = forms.CharField(label="Title", max_length=100)
    slug = forms.SlugField()
    overview = forms.CharField(label="Text", widget=forms.Textarea)
    content = forms.CharField(label="Content", widget=forms.Textarea)
    thumbnail = forms.ImageField(required=False, label="Thumbnail", help_text="Optional")
    categories = forms.MultipleChoiceField(
        choices=[(category.id, category.title) for category in Category.objects.all()],
        required=False,
    )
    status = forms.ChoiceField(choices=StatusType)
