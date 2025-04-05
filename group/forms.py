# forms.py
from django import forms
from .models import (
    InspiGroup,
    InspiGroupNews,
    InspiGroupJoinRequest,
    InspiGroupMembership,
    InspiGroupPermission,
    User,
)

from ckeditor.widgets import CKEditorWidget


class InspiGroupForm(forms.ModelForm):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "Gruppennamen eingeben"}),
        label="Name deiner Gruppe",
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={"placeholder": "Gruppenbeschreibung eingeben"}),
        label="Beschreibung",
    )
    join_code = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={"placeholder": "Beitrittscode eingeben"}),
        label="Beitrittscode",
        help_text="Dieser Code wird verwendet, um der Gruppe beizutreten",
    )
    is_visible = forms.BooleanField(
        required=False,
        label="Sichtbar?",
        help_text="Öffentlich sichtbar für jeden, aber du entscheidest, wer beitreten kann.",
    )
    free_to_join = forms.BooleanField(
        required=False,
        label="Frei beitreten",
        help_text="Jeder kann der Gruppe beitreten, wenn sie gesehen werden kann.",
    )
    editable_by_users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        label="Bearbeitbar von Benutzern",
        help_text="Benutzer, die diese Gruppe bearbeiten dürfen",
    )
    editable_by_groups = forms.ModelMultipleChoiceField(
        queryset=InspiGroup.objects.filter(is_deleted=False),
        required=False,
        label="Bearbeitbar von Gruppen",
        help_text="Gruppen, deren Mitglieder diese Gruppe bearbeiten dürfen",
    )

    class Meta:
        model = InspiGroup
        fields = [
            "name",
            "description",
            "join_code",
            "is_visible",
            "free_to_join",
            "editable_by_users",
            "editable_by_groups",
        ]


class InspiGroupNewsForm(forms.ModelForm):
    subject = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "Betreff eingeben"}),
        label="Betreff",
        required=True,
    )
    message = forms.CharField(
        widget=CKEditorWidget(attrs={"placeholder": "Nachricht eingeben"}),
        label="Nachricht",
        required=True,
    )
    is_visible = forms.BooleanField(
        required=False,
        label="Sichtbar?",
        help_text="Wird dieses News für alle Gruppenmitglieder sichtbar sein?",
    )

    class Meta:
        model = InspiGroupNews
        fields = [
            "subject",
            "message",
            "is_visible",
        ]


class InspiGroupJoinRequestForm(forms.ModelForm):
    class Meta:
        model = InspiGroupJoinRequest
        fields = []


class InspiGroupMembershipMemberForm(forms.ModelForm):
    share_all_personal_data = forms.BooleanField(
        required=False,
        label="Mitflied teilt all persönlichen Daten mit der Gruppe",
        widget=forms.CheckboxInput(),
    )
    share_own_personal_data = forms.BooleanField(
        required=False,
        label="Mitglied teilt nur eigene persönlichen Daten mit der Gruppe",
        widget=forms.CheckboxInput(),
    )

    class Meta:
        model = InspiGroupMembership
        fields = [
            "share_all_personal_data",
            "share_own_personal_data",
        ]


class InspiGroupMembershipAdminForm(forms.ModelForm):
    read_access = forms.BooleanField(
        required=False,
        label="Lese Zugriff auf die persönlichen Daten der Gruppe",
        widget=forms.CheckboxInput(),
    )
    full_access = forms.BooleanField(
        required=False,
        label="Vollen Zugriff auf die persönlichen Daten der Gruppe",
        widget=forms.CheckboxInput(),
    )

    class Meta:
        model = InspiGroupMembership
        fields = [
            "read_access",
            "full_access",
        ]


class InspiGroupPermissionForm(forms.ModelForm):
    class Meta:
        model = InspiGroupPermission
        fields = ["read_access", "full_access"]


class JoinGroupByCodeForm(forms.Form):
    join_code = forms.CharField(max_length=20)


class ManageMembershipForm(forms.ModelForm):
    share_all_personal_data = forms.BooleanField(
        required=False,
        label="Alle persönlichen Daten teilen",
        widget=forms.CheckboxInput(
            attrs={
                "placeholder": "Du teilst nur deine eigenen persönlichen Daten mit der Gruppe.",
            }
        ),
    )
    share_own_personal_data = forms.BooleanField(
        required=False,
        label="Eigene persönliche Daten teilen",
        widget=forms.CheckboxInput(
            attrs={
                "placeholder": "Du teilst nur deine eigenen persönlichen Daten mit der Gruppe.",
            }
        ),
    )

    class Meta:
        model = InspiGroupMembership
        fields = ["share_all_personal_data", "share_own_personal_data"]


class InspiGroupMembershipSearchFilterForm(forms.ModelForm):
    search = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "Suche nach Mitgliedern"}),
        required=False,
        label="",
    )
    is_cancelled = forms.BooleanField(required=False, label="Ausgetreten")
    is_not_cancelled = forms.BooleanField(
        required=False,
        label="Aktive Mitgliedschaft",
    )

    class Meta:
        model = InspiGroupMembership
        fields = [
            "search",
            "is_cancelled",
            "is_not_cancelled",
        ]


class InspiGroupRequestSearchFilterForm(forms.ModelForm):
    search = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "Suche nach Anfragen"}),
        required=False,
        label="",
    )
    approved = forms.BooleanField(required=False, label="Genehmigt")
    not_approved = forms.BooleanField(required=False, label="Nicht genehmigt")

    class Meta:
        model = InspiGroupJoinRequest
        fields = [
            "search",
            "approved",
            "not_approved",
        ]


class InspiGroupPermissionForm(forms.ModelForm):
    read_access = forms.BooleanField(
        required=False,
        label="Leserechte",
        widget=forms.CheckboxInput(
            attrs={
                "placeholder": "Du teilst nur deine eigenen persönlichen Daten mit der Gruppe.",
            }
        ),
    )
    full_access = forms.BooleanField(
        required=False,
        label="Vollzugriff",
        widget=forms.CheckboxInput(
            attrs={
                "placeholder": "Du teilst nur deine eigenen persönlichen Daten mit der Gruppe.",
            }
        ),
    )
    parent_group = forms.ModelChoiceField(
        queryset=InspiGroup.objects.filter(is_deleted=False),
        required=False,
        label="Übergeordnete Gruppe",
    )

    class Meta:
        model = InspiGroupPermission
        fields = ["read_access", "full_access", "parent_group"]


class MyGroupsFilterForm(forms.ModelForm):
    search = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "Suche nach Gruppen..."}),
        required=False,
        label="",
    )
    is_cancelled = forms.BooleanField(required=False, label="Ausgetreten")
    is_not_cancelled = forms.BooleanField(
        required=False,
        label="Aktive Mitgliedschaft",
    )

    class Meta:
        model = InspiGroupMembership
        fields = [
            "search",
            "is_cancelled",
            "is_not_cancelled",
        ]


class GroupListFilter(forms.Form):
    search = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "Suche nach Gruppen..."}),
        required=False,
        label="",
    )
    free_to_join = forms.BooleanField(
        required=False,
        label="Beitretbar?",
    )
    is_visible = forms.BooleanField(
        required=False,
        label="Öffentlich?",
    )
    is_member = forms.BooleanField(
        required=False,
        label="Mitglied?",
    )
    is_not_member = forms.BooleanField(
        required=False,
        label="Kein Mitglied?",
    )
    is_admin = forms.BooleanField(
        required=False,
        label="Admin?",
    )


class MyRequestsFilterForm(forms.Form):
    search = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "Suche nach Anfragen..."}),
        required=False,
        label="",
    )
    approved = forms.BooleanField(
        required=False,
        label="Genehmigt",
    )
    not_approved = forms.BooleanField(
        required=False,
        label="Nicht genehmigt",
    )

    class Meta:
        model = InspiGroupJoinRequest
        fields = [
            "search",
            "approved",
            "not_approved",
        ]


class InspiGroupsFilterForm(forms.Form):
    search = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "Suche nach Gruppen"}),
        required=False,
    )

    class Meta:
        model = InspiGroup
        fields = [
            "search",
        ]


class ChildGroupsFilterForm(forms.ModelForm):
    search = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "Suche nach Gruppen"}),
        required=False,
        label="",
    )

    class Meta:
        model = InspiGroup
        fields = [
            "search",
        ]


class ParentGroupsFilterForm(forms.ModelForm):
    search = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "Suche nach Gruppen"}),
        required=False,
        label="",
    )

    class Meta:
        model = InspiGroup
        fields = [
            "search",
        ]


class InspiGroupAdminSearchFilterForm(forms.ModelForm):
    search = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "Suche nach Gruppen"}),
        required=False,
        label="",
    )

    class Meta:
        model = InspiGroup
        fields = [
            "search",
        ]


class InspiGroupAddMembershipForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label="Benutzer",
        widget=forms.HiddenInput(),
    )

    class Meta:
        model = InspiGroupMembership
        fields = ["user"]
