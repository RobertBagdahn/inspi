from django import forms
from .models import MessageType, Message, Faq
from ckeditor.widgets import CKEditorWidget


class MessageForm(forms.ModelForm):
    name = forms.CharField(
        max_length=50,
        label="Dein Name",
    )
    email = forms.EmailField(
        label="Deine E-Mail für Rückfragen",
        required=False,
    )
    type = forms.ModelChoiceField(
        queryset=MessageType.objects.all(),
        empty_label="Bitte wähle eine Option",
        label="Art der Nachricht",
    )
    subject = forms.CharField(
        max_length=100,
        label="Betreff",
    )

    body = forms.CharField(
        widget=forms.Textarea,
        label="Deine Nachricht an Inspi",
        help_text="Bitte beschreibe dein Anliegen so genau wie möglich."
    )


    class Meta:
        model = Message
        fields = ["name", "email", "type", "subject", "body"]



class FaqForm(forms.ModelForm):
    question = forms.CharField(max_length=200)
    answer = forms.CharField(widget=forms.Textarea)
    sorting = forms.IntegerField()

    class Meta:
        model = Faq
        fields = ["question", "answer", "sorting"]

class FaqQuestionForm(forms.Form):
    question = forms.CharField(
        widget=CKEditorWidget(attrs={"class": "col-span-2"}),
        max_length=200,
        label="Deine Frage",
        required=True,
        help_text="Stelle hier deine Frage."
    )
    answer = forms.HiddenInput()
    sorting = forms.HiddenInput()

    class Meta:
        model = Faq
        fields = ["question", "answer", "sorting"]