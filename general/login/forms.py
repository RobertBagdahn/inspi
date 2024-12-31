from allauth.account.forms import LoginForm, SignupForm

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
from group.models import InspiGroupMembership


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

    scout_display_name = forms.CharField(max_length=50, label="Scout Display Name")

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
