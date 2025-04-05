from django.shortcuts import render
from .models import CustomUser
from .forms import CustomUserChangeForm, InspiGroupAdminSearchFilterForm
from group.forms import MyRequestsFilterForm
import random, string
from django.contrib.sessions.models import Session
from django.contrib.auth.decorators import login_required

from group.models import InspiGroup, InspiGroupMembership, InspiGroupJoinRequest, InspiGroupPermission
from django.core.paginator import Paginator
from formtools.wizard.views import SessionWizardView
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.decorators import method_decorator
from .forms import (
    PersonWizardIntroForm, 
    PersonWizardBasicInfoForm, 
    PersonWizardContactForm, 
    PersonWizardPreferencesForm
)
from .models import Person

def randomword(length):
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(length))



def profile_edit(request, username):
    user = CustomUser.objects.get(username=username)
    form = CustomUserChangeForm(instance=user)

    if request.method == "POST":
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return render(request, "user-profile.html", {"user": user})

    context = {
        "user": user,
        "form": form,
    }

    return render(request, "profile-edit.html", context)


def profile_delete(request, username):
    user = CustomUser.objects.get(username=username)

    if request.method == "POST":
        user.email = "deleted"
        user.scout_display_name = randomword(20)
        user.stamm = "deleted"
        user.bund = "deleted"
        user.about_me = "deleted"
        user.is_active = False
        [s.delete() for s in Session.objects.all() if s.get_decoded().get('_auth_user_id') == user.id]
        user.save()

        return render(request, "user-profile.html", {
            "user": user,
            "deleted": True,
        })

    return render(request, "profile-delete.html", {
        "user": user,
        "deleted": False,
    })

def settings(request, username):
    user = CustomUser.objects.get(username=username)
    is_stuff = request.user.is_staff

    context = {
        "user": user,
        "is_stuff": is_stuff,
    }
    return render(request, "settings.html", context)


def user_detail_overview(request, username):
    user = CustomUser.objects.get(username=username)

    search_filter_form = InspiGroupAdminSearchFilterForm(request.GET)

    # get all inspi groups
    kpi_membershps = InspiGroupMembership.objects.filter(user=user, is_cancelled=False).count()

    items_basic = [
        {"title": "Anzeigename", "value": user.scout_display_name},
        {"title": "E-Mail", "value": user.email},
        {"title": "Registrierungsdatum", "value": user.date_joined},
        {"title": "Letzter Login", "value": user.last_login},
    ]
    if user.is_staff:
        items_basic.append(
            {"title": "Ist Admin", "value": "Ja" if user.is_staff else "Nein"}
        )

    if user.is_superuser:
        items_basic.append(
            {"title": "Ist Superuser", "value": "Ja" if user.is_superuser else "Nein"}
        )

    if user.person:
        items_personal = [
            {"title": "Vorname", "value": user.person.first_name},
            {"title": "Nachname", "value": user.person.last_name},
            {"title": "Geburtstag", "value": user.person.birthday},
            {"title": "Handynummer", "value": user.person.mobile},
            {"title": "Pfadfindergruppe", "value": user.person.scout_group},
            {"title": "Pfadfindername", "value": user.person.scout_name},
            {"title": "Adresse", "value": user.person.address},
            {"title": "Adresszusatz", "value": user.person.address_supplement},
            {"title": "Postleitzahl", "value": user.person.zip_code},
            {"title": "Stadt", "value": user.person.city},
            {"title": "Geschlecht", "value": user.person.get_gender_display()},
            {"title": "Essgewohnheiten", "value": user.person.get_eat_habits_display()},
            {"title": "Über mich", "value": user.person.about_me},
            {"title": "Stamm", "value": user.person.stamm},
            {"title": "Bund", "value": user.person.bund},
        ]
    else:
        items_personal = []

    # editable  when stuff or user is the same as the user
    editable = False
    if request.user.is_staff or request.user == user:
        editable = True


    return render(request, "user-detail/overview/main.html", {
        "user": user,
        "deleted": False,
        "items_basic": items_basic,
        "items_personal": items_personal,
        "kpi_membershps": kpi_membershps,
        "editable": editable,
        "search_filter_form": search_filter_form
    })

def user_detail_manage(request, username):
    user = CustomUser.objects.get(username=username)

    return render(request, "user-detail/manage/main.html", {
        "user": user,
        "deleted": False,
    })


def user_detail_memberships(request, username):
    user = CustomUser.objects.get(username=username)
    memberships = InspiGroupMembership.objects.filter(user=user)
    search_filter_form = InspiGroupAdminSearchFilterForm(request.GET)

    paginator = Paginator(memberships, 10)  # Show 10 memberships per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        "user": user,
        "deleted": False,
        "page_obj": page_obj,
        "search_filter_form": search_filter_form,
    }

    return render(request, "user-detail/memberships/main.html", context)


def user_detail_person(request, username):
    user = CustomUser.objects.get(username=username)

    return render(request, "user-detail/person/main.html", {
        "user": user,
        "deleted": False,
    })


def user_dashboard(request):
    user = CustomUser.objects.get(username=request.user.username)

    return render(request, "user-dashboard/main.html", {
        "user": user,
        "deleted": False,
    })


def user_list(request):
    users = CustomUser.objects.all()

    paginator = Paginator(users, 10)  # Show 10 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "user-list/main.html", {
        "page_obj": page_obj,
        "users": users,
    })



@login_required
def user_detail_my_requests_user(request, username):
    user = CustomUser.objects.get(username=username)
    # check if user is the same as the user in the url or is staff or superuser
    if not request.user.is_staff and not request.user.is_superuser and request.user != user:
        return render(request, "403.html")
    requests = InspiGroupJoinRequest.objects.filter(user=user)
    form = MyRequestsFilterForm(request.GET)

    if form.is_valid():
        requests = requests.filter(
            group__name__icontains=form.cleaned_data.get("search", "")
        )
        if form.cleaned_data.get("approved"):
            requests = requests.filter(approved=True)
        if form.cleaned_data.get("not_approved"):
            requests = requests.filter(approved=False)

    paginator = Paginator(requests, 10)  # Show 10 requests per page.
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "user-detail/my-requests/main.html",
        {
            "page_obj": page_obj,
            "form": form,
        },
    )

# Define wizard steps
PERSON_WIZARD_FORMS = [
    ('intro', PersonWizardIntroForm),
    ('basic_info', PersonWizardBasicInfoForm),
    ('contact', PersonWizardContactForm),
    ('preferences', PersonWizardPreferencesForm),
]

# Define step titles and descriptions
PERSON_WIZARD_TEMPLATES = {
    'intro': {
        'template': 'person/wizard/0-intro-step.html',
        'title': 'Willkommen zum Profil-Wizard',
        'description': 'Mit diesem Wizard kannst du deine persönlichen Daten einfach und strukturiert eingeben.',
    },
    'basic_info': {
        'template': 'person/wizard/generic_step.html',
        'title': 'Grundlegende Informationen',
        'description': 'Hier kannst du deine grundlegenden persönlichen Daten eingeben.',
    },
    'contact': {
        'template': 'person/wizard/generic_step.html',
        'title': 'Kontaktinformationen',
        'description': 'Hier kannst du deine Kontaktdaten eingeben.',
    },
    'preferences': {
        'template': 'person/wizard/generic_step.html',
        'title': 'Präferenzen & weitere Informationen',
        'description': 'Hier kannst du weitere Informationen zu deinen Präferenzen eingeben.',
    },
}

@method_decorator(login_required, name='dispatch')
class PersonWizardView(SessionWizardView):
    form_list = PERSON_WIZARD_FORMS
    
    def get_template_names(self):
        return [PERSON_WIZARD_TEMPLATES[self.steps.current]['template']]
    
    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        current_step = self.steps.current
        
        # Add step title and description to context
        context.update({
            'step_title': PERSON_WIZARD_TEMPLATES[current_step]['title'],
            'step_description': PERSON_WIZARD_TEMPLATES[current_step]['description'],
            'total_steps': len(self.form_list),
        })
        
        # Add user data if editing existing Person
        if hasattr(self, 'person_instance') and self.person_instance:
            context['person'] = self.person_instance
        
        return context
    
    def get_form_initial(self, step):
        initial = self.initial_dict.get(step, {})
        
        # If editing an existing Person, pre-fill form fields
        if hasattr(self, 'person_instance') and self.person_instance:
            person = self.person_instance
            
            if step == 'basic_info':
                initial.update({
                    'first_name': person.first_name,
                    'last_name': person.last_name,
                    'scout_name': person.scout_name,
                    'gender': person.gender,
                    'birthday': person.birthday,
                })
            elif step == 'contact':
                initial.update({
                    'address': person.address,
                    'address_supplement': person.address_supplement,
                    'zip_code': person.zip_code,
                    'city': person.city,
                    'mobile': person.mobile,
                })
            elif step == 'preferences':
                initial.update({
                    'eat_habits': person.eat_habits,
                    'scout_group': person.scout_group,
                    'about_me': person.about_me,
                })
        
        return initial
    
    def dispatch(self, request, *args, **kwargs):
        # If editing an existing person, get the instance
        username = kwargs.get('username')
        if username:
            user = CustomUser.objects.get(username=username)
            # Get or create person instance
            if user.person:
                self.person_instance = user.person
            else:
                # Create a new Person if user doesn't have one yet
                self.person_instance = None
        
        return super().dispatch(request, *args, **kwargs)
    
    def done(self, form_list, **kwargs):
        # Process the completed forms and save the data
        form_data = self.get_all_cleaned_data()
        
        # Get or create person instance
        username = kwargs.get('username', self.request.user.username)
        user = CustomUser.objects.get(username=username)
        
        if user.person:
            person = user.person
        else:
            person = Person()
            
        # Update person fields from form data
        person.first_name = form_data.get('first_name', '')
        person.last_name = form_data.get('last_name', '')
        person.scout_name = form_data.get('scout_name')
        person.gender = form_data.get('gender')
        person.birthday = form_data.get('birthday')
        person.address = form_data.get('address')
        person.address_supplement = form_data.get('address_supplement')
        person.zip_code = form_data.get('zip_code')
        person.city = form_data.get('city')
        person.mobile = form_data.get('mobile')
        person.eat_habits = form_data.get('eat_habits')
        person.scout_group = form_data.get('scout_group')
        person.about_me = form_data.get('about_me')
        
        # Save the person
        person.save()
        
        # Link to user if needed
        if not user.person:
            user.person = person
            user.save()
        
        messages.success(self.request, "Deine persönlichen Daten wurden erfolgreich gespeichert!")
        return redirect('user-detail-overview', username=username)

@login_required
def start_person_wizard(request, username=None):
    # Validate the user has permission to edit this profile
    if username and username != request.user.username:
        if not request.user.is_staff and not request.user.is_superuser:
            return render(request, "403.html")
    
    # If no username provided, use the current user
    if not username:
        username = request.user.username
    
    # Redirect to the wizard view
    return redirect('person-wizard', username=username)
