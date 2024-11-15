# test/forms.py
from django import forms
from .choices import ColorType

class ImageDownloadForm(forms.Form):

	document_type = forms.ChoiceField(
		label='Dokumenttyp',
		choices=[('insta', 'Instagram'), ('a4', 'A4-Seite')],
		widget=forms.RadioSelect(attrs={"class": "tailwind-radio"}),
		required=True,
		help_text='Wählen Sie den Dokumenttyp aus.',
		initial='insta'
	)

	color = forms.ChoiceField(
		label='Farbe',
		choices=ColorType.choices,
		widget=forms.RadioSelect(attrs={"class": "tailwind-radio"}),
		required=False,
		help_text='Wählen Sie eine Hintergrund aus.',
		initial=ColorType.RED
	)

	page = forms.IntegerField(
		label='Seite',
		required=True,
		widget=forms.RadioSelect(
			attrs={"class": "tailwind-radio"},
			choices=[(1, 1), (2, 2), (3, 3)],
		),
		help_text='Geben Sie die Seitenzahl an.',
		initial=1
	)