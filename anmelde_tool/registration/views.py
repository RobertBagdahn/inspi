from anmelde_tool.event.basic.models import (
    Event,
    EventPermission,
    EventModule,
)
import csv
from django.http import HttpResponse
import csv
from django.http import HttpResponse
from general.login.forms import PersonForm
from .models import Registration, RegistrationParticipant
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse
from formtools.wizard.views import SessionWizardView
from django.contrib import messages
from django.utils.decorators import method_decorator
from .forms import (
    RegistrationListFilter,
    RegistrationBaseForm,
    ParticipantForm,
    ScoutGroupForm,
    ParticipantSearchForm,
    PrivacySearchForm,
)
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO
from datetime import date
from anmelde_tool.event.basic.models import EventRegistrationType
from general.login.models import CustomUser
from anmelde_tool.attributes.models import (
    AttributeModule,
    BooleanAttribute,
    StringAttribute,
    DateTimeAttribute,
    IntegerAttribute,
    FloatAttribute,
    TravelAttribute,
)
from masterdata import models as basic_models
from anmelde_tool.registration.forms import create_module_form_class
from anmelde_tool.event.email.helper import event_email_send_confirmation
from django.utils import timezone
from .forms import RegistrationRevocationForm


@login_required
def register_detail_overview(request, reg_id):
    """
    View for managing registration details.
    """
    register = get_object_or_404(Registration, id=reg_id)
    event = register.event

    kpi_participants = register.participant_count
    kpi_cost = 123
    kpi_responsible_persons = register.responsible_persons.count()
    kpi_attributes = 43

    return render(
        request,
        "registration_detail/overview/main.html",
        {
            "event": event,
            "reg": register,
            "kpi_participants": kpi_participants,
            "kpi_cost": kpi_cost,
            "kpi_responsible_persons": kpi_responsible_persons,
            "kpi_attributes": kpi_attributes,
            "breadcrumbs": [
                {"name": "Alle Veranstaltungen", "url": reverse("event-list")},
                {
                    "name": event.name,
                    "url": reverse("event-detail-overview", args=[event.slug]),
                },
                {
                    "name": "Anmeldung",
                    "url": reverse("reg-detail-overview", args=[register.id]),
                },
                {"name": "Übersicht", "url": "#"},
            ],
        },
    )


@login_required
def register_detail_attribute(request, reg_id):
    """
    View for managing event modules.
    """
    register = get_object_or_404(Registration, id=reg_id)
    event = register.event
    event_modules = EventModule.objects.filter(event=event).order_by("ordering")

    # Prepare a dictionary to store modules and their attributes
    modules_data = []

    for module in event_modules:
        module_data = {"module": module, "attributes": []}

        # Get all attribute modules associated with this event module
        attribute_modules = AttributeModule.objects.filter(event_module=module)

        for attr_module in attribute_modules:
            attribute_data = {
                "attribute_module": attr_module,
                "value": None,
                "type": attr_module.get_field_type_display(),
            }

            # Get the attribute value based on its type
            if attr_module.field_type == "BoA":

                try:
                    boolean_attr = BooleanAttribute.objects.get(
                        attribute_module=attr_module, registration=register
                    )
                    if boolean_attr:
                        attribute_data["value"] = boolean_attr.boolean_field
                        attribute_data["id"] = boolean_attr.id
                        print(f"Boolean Attribute: {boolean_attr.boolean_field}")
                except BooleanAttribute.DoesNotExist:
                    pass

            elif attr_module.field_type == "StA":
                try:
                    string_attr = StringAttribute.objects.get(
                        attribute_module=attr_module, registration=register
                    )
                    attribute_data["value"] = string_attr.string_field
                    attribute_data["id"] = string_attr.id
                except StringAttribute.DoesNotExist:
                    pass

            elif attr_module.field_type == "TiA":
                try:
                    datetime_attr = DateTimeAttribute.objects.first()
                    attribute_data["value"] = datetime_attr.date_time_field
                    attribute_data["id"] = datetime_attr.id
                except DateTimeAttribute.DoesNotExist:
                    pass

            elif attr_module.field_type == "InA":
                try:
                    integer_attr = IntegerAttribute.objects.get(
                        attribute_module=attr_module, registration=register
                    )
                    attribute_data["value"] = integer_attr.integer_field
                    attribute_data["id"] = integer_attr.id
                except IntegerAttribute.DoesNotExist:
                    pass

            elif attr_module.field_type == "FlA":
                try:
                    float_attr = FloatAttribute.objects.get(
                        attribute_module=attr_module, registration=register
                    )
                    attribute_data["value"] = float_attr.float_field
                    attribute_data["id"] = float_attr.id
                except FloatAttribute.DoesNotExist:
                    pass

            elif attr_module.field_type == "TrA":
                try:
                    travel_attr = TravelAttribute.objects.filter(
                        attribute_module=attr_module, registration=register
                    ).first()
                    if travel_attr:
                        attribute_data["value"] = {
                            "number_persons": travel_attr.number_persons,
                            "type_field": travel_attr.type_field,
                            "date_time_field": travel_attr.date_time_field,
                            "description": travel_attr.description,
                        }
                        attribute_data["id"] = travel_attr.id
                except TravelAttribute.DoesNotExist:
                    pass
                except AttributeError:
                    pass

            module_data["attributes"].append(attribute_data)

        modules_data.append(module_data)

    return render(
        request,
        "registration_detail/attribute/main.html",
        {
            "event": event,
            "reg": register,
            "modules_data": modules_data,
            "breadcrumbs": [
                {"name": "Alle Veranstaltungen", "url": reverse("event-list")},
                {
                    "name": event.name,
                    "url": reverse("event-detail-overview", args=[event.slug]),
                },
                {
                    "name": "Anmeldung",
                    "url": reverse("reg-detail-overview", args=[register.id]),
                },
                {"name": "Verwalten", "url": "#"},
            ],
        },
    )


@login_required
def register_detail_permission(request, reg_id):
    """
    View for managing registration permissions.
    """
    register = get_object_or_404(Registration, id=reg_id)
    event = register.event

    return render(
        request,
        "registration_detail/permission/main.html",
        {
            "event": event,
            "reg": register,
            "breadcrumbs": [
                {"name": "Alle Veranstaltungen", "url": reverse("event-list")},
                {
                    "name": event.name,
                    "url": reverse("event-detail-overview", args=[event.slug]),
                },
                {
                    "name": "Anmeldung",
                    "url": reverse("reg-detail-overview", args=[register.id]),
                },
                {
                    "name": "Berechtigungen",
                    "url": reverse("reg-detail-permission", args=[register.id]),
                },
            ],
        },
    )


@login_required
def add_responsible_person(request, reg_id):
    """
    View for adding a new responsible person to a registration.
    """
    registration = get_object_or_404(Registration, id=reg_id)

    if request.method == "POST":
        # Get the user ID from the form
        user_id = request.POST.get("user_id")

        if user_id:
            try:
                from django.contrib.auth import get_user_model

                User = get_user_model()
                user = User.objects.get(id=user_id)

                # Add the user to responsible_persons if not already there
                if user not in registration.responsible_persons.all():
                    registration.responsible_persons.add(user)
                    messages.success(
                        request,
                        f"{user.scout_display_name} wurde als verantwortliche Person hinzugefügt.",
                    )
                else:
                    messages.info(
                        request,
                        f"{user.scout_display_name} ist bereits eine verantwortliche Person.",
                    )
            except User.DoesNotExist:
                messages.error(request, "Benutzer nicht gefunden.")
        else:
            messages.error(request, "Kein Benutzer ausgewählt.")

        return redirect("reg-detail-permission", reg_id=reg_id)

    # Get users who aren't already responsible persons
    current_responsible_persons = registration.responsible_persons.all()
    available_users = CustomUser.objects.exclude(
        id__in=current_responsible_persons.values_list("id", flat=True)
    )

    return render(
        request,
        "registration_detail/permission/add_responsible_person.html",
        {
            "event": registration.event,
            "reg": registration,
            "available_users": available_users,
            "breadcrumbs": [
                {"name": "Alle Veranstaltungen", "url": reverse("event-list")},
                {
                    "name": registration.event.name,
                    "url": reverse(
                        "event-detail-overview", args=[registration.event.slug]
                    ),
                },
                {
                    "name": "Anmeldung",
                    "url": reverse("reg-detail-overview", args=[registration.id]),
                },
                {
                    "name": "Berechtigungen",
                    "url": reverse("reg-detail-permission", args=[registration.id]),
                },
                {"name": "Neue Person berechtigen", "url": "#"},
            ],
        },
    )


@login_required
def remove_responsible_person(request, reg_id, person_id):
    """
    View for removing a responsible person from a registration.
    """
    if request.method == "POST":
        registration = get_object_or_404(Registration, id=reg_id)

        # Check if the current user has permission to modify responsible persons
        if (
            not request.user.is_superuser
            and request.user != registration.responsible_persons.first()
        ):
            messages.error(
                request,
                "Du hast keine Berechtigung, verantwortliche Personen zu entfernen.",
            )
            return redirect("reg-detail-permission", reg_id=reg_id)

        # Get the person to remove
        try:
            from django.contrib.auth import get_user_model

            User = get_user_model()
            person = User.objects.get(id=person_id)

            # Remove the person from the responsible_persons field
            registration.responsible_persons.remove(person)
            messages.success(
                request,
                f"{person.scout_display_name} wurde als verantwortliche Person entfernt.",
            )
        except User.DoesNotExist:
            messages.error(request, "Person nicht gefunden.")

    return redirect("reg-detail-permission", reg_id=reg_id)


@login_required
def register_detail_participant(request, reg_id):
    """
    View for managing registration participants.
    """
    reg = get_object_or_404(Registration, id=reg_id)
    event = reg.event

    # Get participants for this registration
    participants = reg.participants.all()

    # Set up pagination
    paginator = Paginator(participants, 10)  # Show 10 participants per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "registration_detail/participant/main.html",
        {
            "event": event,
            "reg": reg,
            "page_obj": page_obj,
            "form": ParticipantSearchForm(event=event, reg=reg),
            "breadcrumbs": [
                {"name": "Alle Veranstaltungen", "url": reverse("event-list")},
                {
                    "name": event.name,
                    "url": reverse("event-detail-overview", args=[event.slug]),
                },
                {
                    "name": "Anmeldung",
                    "url": reverse("reg-detail-overview", args=[reg.id]),
                },
                {
                    "name": "Teilnehmende",
                    "url": reverse("reg-detail-participant", args=[reg.id]),
                },
            ],
        },
    )


@login_required
def participant_create(request, reg_id):
    """
    View for creating a new participant for a registration.
    """
    reg = get_object_or_404(Registration, id=reg_id)
    event = reg.event

    if request.method == "POST":
        form = ParticipantForm(request.POST, registration_id=reg_id, event=event)
        if form.is_valid():
            # Create the participant manually from form data
            zip_code_str = form.cleaned_data["zip_code"]
            if zip_code_str:
                zip_code_instance = get_object_or_404(
                    basic_models.ZipCode, zip_code=zip_code_str
                )
            else:
                zip_code = None
            participant = RegistrationParticipant(
                registration=reg,
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
                address=form.cleaned_data["address"],
                zip_code=zip_code_instance,
                birthday=form.cleaned_data["birthday"],
                gender=form.cleaned_data["gender"],
                scout_name=form.cleaned_data.get("scout_name", ""),
            )
            participant.save()

            # Handle many-to-many relationships if needed
            if "eat_habit" in form.cleaned_data:
                participant.eat_habit.set(form.cleaned_data["eat_habit"])

            messages.success(request, "Teilnehmer*in erfolgreich erstellt!")
            return redirect("reg-detail-participant", reg_id=reg.id)
    else:
        form = ParticipantForm(request.POST, registration_id=reg_id, event=event)
    return render(
        request,
        "participant/create/main.html",
        {
            "event": event,
            "reg": reg,
            "form": form,
            "breadcrumbs": [
                {"name": "Alle Veranstaltungen", "url": reverse("event-list")},
                {
                    "name": event.name,
                    "url": reverse("event-detail-overview", args=[event.slug]),
                },
                {
                    "name": "Anmeldung",
                    "url": reverse("reg-detail-overview", args=[reg.id]),
                },
                {
                    "name": "Teilnehmende",
                    "url": reverse("reg-detail-participant", args=[reg.id]),
                },
                {"name": "Neu", "url": "#"},
            ],
        },
    )


@login_required
def participant_update(request, reg_id, participant_id):
    """
    View for updating an existing participant.
    """
    reg = get_object_or_404(Registration, id=reg_id)
    event = reg.event
    participant = get_object_or_404(
        RegistrationParticipant, id=participant_id, registration=reg
    )

    if request.method == "POST":
        form = ParticipantForm(
            request.POST,
            registration_id=reg_id,
            event=event,
        )
         # Check if the form is valid
         # If the form is valid, save the participant
        
        if form.is_valid():
            
            # Handle zip_code separately to ensure it's a ZipCode instance
            zip_code_value = form.cleaned_data.get('zip_code')
            if zip_code_value:
                if isinstance(zip_code_value, str):
                    try:
                        zip_code_instance = get_object_or_404(basic_models.ZipCode, zip_code=zip_code_value)
                        participant.zip_code = zip_code_instance
                    except:
                        participant.zip_code = None
                # If it's already a ZipCode instance, it will be handled correctly

            # Update participant fields from form data
            participant.first_name = form.cleaned_data['first_name']
            participant.last_name = form.cleaned_data['last_name']
            participant.address = form.cleaned_data['address']
            participant.birthday = form.cleaned_data['birthday']
            participant.gender = form.cleaned_data['gender']
            participant.scout_name = form.cleaned_data.get('scout_name', '')

            # Handle zip_code - this has already been processed in the code before the placeholder

            # Handle many-to-many relationships
            # if 'eat_habit' in form.cleaned_data and form.cleaned_data['eat_habit']:
            #     # Make sure we're dealing with ID values, not string names
            #     # If the values are already model instances, set() will handle them correctly
            #     # If they're IDs, they'll also work correctly
            #     # If they might be strings, we need to resolve them to proper model instances or IDs
            #     participant.eat_habit.clear()
            #     for habit in form.cleaned_data['eat_habit']:
            #         if isinstance(habit, int):
            #             participant.eat_habit.add(habit.id)
            #         elif hasattr(habit, 'id'):
            #             participant.eat_habit.add(habit.id)

            # Handle scout_level if it's in the form
            if 'scout_level' in form.cleaned_data and form.cleaned_data['scout_level']:
                participant.scout_level = form.cleaned_data['scout_level']

            # Save the updated participant
            participant.save()
            
            
            messages.success(request, "Teilnehmer*in erfolgreich aktualisiert!")
            return redirect("reg-detail-participant", reg_id=reg.id)
    else:
        # Initialize with initial data instead of instance since this is not a ModelForm
        initial_data = {
            'first_name': participant.first_name,
            'last_name': participant.last_name,
            'address': participant.address,
            'zip_code': participant.zip_code.zip_code if participant.zip_code else None,
            'birthday': participant.birthday,
            'gender': participant.gender,
            'scout_name': participant.scout_name,
            'eat_habit': participant.eat_habit.all(),
            'scout_level': participant.scout_level,
        }
        form = ParticipantForm(
            initial=initial_data,
            registration_id=reg_id,
            event=event,
        )

    return render(
        request,
        "participant/update/main.html",
        {
            "event": event,
            "reg": reg,
            "participant": participant,
            "form": form,
            "breadcrumbs": [
                {"name": "Alle Veranstaltungen", "url": reverse("event-list")},
                {
                    "name": event.name,
                    "url": reverse("event-detail-overview", args=[event.slug]),
                },
                {
                    "name": "Anmeldung",
                    "url": reverse("reg-detail-overview", args=[reg.id]),
                },
                {
                    "name": "Teilnehmende",
                    "url": reverse("reg-detail-participant", args=[reg.id]),
                },
                {"name": "Bearbeiten", "url": "#"},
            ],
        },
    )


@login_required
def participant_detail(request, reg_id, participant_id):
    """
    View for viewing participant details.
    """
    reg = get_object_or_404(Registration, id=reg_id)
    event = reg.event
    participant = get_object_or_404(
        RegistrationParticipant, id=participant_id, registration=reg
    )

    return render(
        request,
        "participant/detail/main.html",
        {
            "event": event,
            "reg": reg,
            "participant": participant,
            "breadcrumbs": [
                {"name": "Alle Veranstaltungen", "url": reverse("event-list")},
                {
                    "name": event.name,
                    "url": reverse("event-detail-overview", args=[event.slug]),
                },
                {
                    "name": "Anmeldung",
                    "url": reverse("reg-detail-overview", args=[reg.id]),
                },
                {
                    "name": "Teilnehmende",
                    "url": reverse("reg-detail-participant", args=[reg.id]),
                },
                {
                    "name": f"{participant.first_name} {participant.last_name}",
                    "url": "#",
                },
            ],
        },
    )


@login_required
def participant_delete(request, reg_id, participant_id):
    """
    View for deleting a participant.
    """
    reg = get_object_or_404(Registration, id=reg_id)
    participant = get_object_or_404(
        RegistrationParticipant, id=participant_id, registration=reg
    )

    if request.method == "POST":
        participant.delete()
        messages.success(request, "Teilnehmer*in erfolgreich gelöscht!")
        return redirect("reg-detail-participant", reg_id=reg.id)

    return render(
        request,
        "participant/delete/main.html",
        {
            "event": reg.event,
            "reg": reg,
            "participant": participant,
            "breadcrumbs": [
                {"name": "Alle Veranstaltungen", "url": reverse("event-list")},
                {
                    "name": reg.event.name,
                    "url": reverse("event-detail-overview", args=[reg.event.slug]),
                },
                {
                    "name": "Anmeldung",
                    "url": reverse("reg-detail-overview", args=[reg.id]),
                },
                {
                    "name": "Teilnehmende",
                    "url": reverse("reg-detail-participant", args=[reg.id]),
                },
                {"name": "Löschen", "url": "#"},
            ],
        },
    )


@login_required
def register_detail_privacy(request, reg_id):
    """
    View for managing registration privacy settings.
    """
    register = get_object_or_404(Registration, id=reg_id)
    event = register.event

    permissions = EventPermission.objects.filter(
        event=event,
    )

    # Get all users with permissions for this event
    users_with_permissions = set()

    # Add users directly assigned to permissions
    for permission in permissions:
        users_with_permissions.add(permission.user)

    # Add users from groups assigned to permissions
    for permission in permissions:
        if permission.group:
            # Handle custom group model that might have a different attribute for users
            if hasattr(permission.group, "user_set"):
                users_with_permissions.update(permission.group.user_set.all())
            elif hasattr(permission.group, "users"):
                users_with_permissions.update(permission.group.users.all())
            elif hasattr(permission.group, "members"):
                users_with_permissions.update(permission.group.members.all())

    # Convert set to list for pagination
    event_permissions = list(users_with_permissions)

    # Set up pagination
    paginator = Paginator(event_permissions, 10)  # Show 10 users per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    breadcrumbs = [
        {"name": "Alle Veranstaltungen", "url": reverse("event-list")},
        {
            "name": event.name,
            "url": reverse("event-detail-overview", args=[event.slug]),
        },
        {
            "name": "Anmeldung",
            "url": reverse("reg-detail-overview", args=[register.id]),
        },
        {"name": "Datenschutz", "url": "#"},
    ]

    return render(
        request,
        "registration_detail/privacy/main.html",
        {
            "event": event,
            "reg": register,
            "page_obj": page_obj,
            "form": PrivacySearchForm(),
            "breadcrumbs": breadcrumbs,
        },
    )


@login_required
def register_detail_manage(request, reg_id):
    """
    View for managing registration settings and configuration.
    """
    register = get_object_or_404(Registration, id=reg_id)
    event = register.event

    if request.method == "POST":
        form = RegistrationBaseForm(request.POST, instance=register)
        if form.is_valid():
            form.save()
            messages.success(request, "Die Anmeldung wurde erfolgreich aktualisiert.")
            return redirect("reg-detail-overview", reg_id=reg_id)
    else:
        form = RegistrationBaseForm(instance=register)

    return render(
        request,
        "registration_detail/manage/main.html",
        {
            "event": event,
            "reg": register,
            "form": form,
            "breadcrumbs": [
                {"name": "Alle Veranstaltungen", "url": reverse("event-list")},
                {
                    "name": event.name,
                    "url": reverse("event-detail-overview", args=[event.slug]),
                },
                {
                    "name": "Anmeldung",
                    "url": reverse("reg-detail-overview", args=[register.id]),
                },
                {"name": "Verwaltung", "url": "#"},
            ],
        },
    )


@login_required
def registration_list(request):
    """
    View for listing registrations with filtering options.
    """
    if not request.GET:
        request.GET = request.GET.copy()

    # Create a filter form for registrations (you need to implement this form)
    search_filter_form = RegistrationListFilter(request.GET)
    registrations = Registration.objects.all()

    # If you implement a filter form, you can use it like this:
    if search_filter_form.is_valid():
        registrations = registrations.filter(
            event__name__icontains=search_filter_form.cleaned_data.get("query", "")
        )

    # Filter for registrations where the user is responsible
    registrations = registrations.filter(responsible_persons=request.user)

    # Add additional properties if needed
    for registration in registrations:
        registration.event_name = registration.event.name

    paginator = Paginator(registrations, 10)  # Show 10 registrations per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    form = RegistrationListFilter(request.GET)
    return render(
        request,
        "registration_list/main.html",
        {
            "page_obj": page_obj,
            "form": form,
        },
    )


@login_required
def registration_boolean_attribute_create(request, registration_pk):
    """API view to create or update a boolean attribute."""
    if request.method == "POST":
        registration = get_object_or_404(Registration, id=registration_pk)
        attribute_module_id = request.POST.get("attribute_module")
        attribute_module = get_object_or_404(AttributeModule, id=attribute_module_id)

        boolean_value = request.POST.get("boolean_field") == "true"

        # Try to get existing attribute or create new one
        try:
            attribute = BooleanAttribute.objects.get(
                attribute_module=attribute_module, registration=registration
            )
            attribute.boolean_field = boolean_value
            attribute.save()
        except BooleanAttribute.DoesNotExist:
            attribute = BooleanAttribute.objects.create(
                attribute_module=attribute_module,
                registration=registration,
                boolean_field=boolean_value,
            )

        return JsonResponse(
            {"id": attribute.id, "boolean_field": attribute.boolean_field}
        )
    return JsonResponse({"error": "Only POST method is allowed"}, status=405)


@login_required
def registration_string_attribute_create(request, registration_pk):
    """API view to create or update a string attribute."""
    if request.method == "POST":
        registration = get_object_or_404(Registration, id=registration_pk)
        attribute_module_id = request.POST.get("attribute_module")
        attribute_module = get_object_or_404(AttributeModule, id=attribute_module_id)

        string_value = request.POST.get("string_field", "")

        # Try to get existing attribute or create new one
        try:
            attribute = StringAttribute.objects.get(
                attribute_module=attribute_module, registration=registration
            )
            attribute.string_field = string_value
            attribute.save()
        except StringAttribute.DoesNotExist:
            attribute = StringAttribute.objects.create(
                attribute_module=attribute_module,
                registration=registration,
                string_field=string_value,
            )

        return JsonResponse(
            {"id": attribute.id, "string_field": attribute.string_field}
        )
    return JsonResponse({"error": "Only POST method is allowed"}, status=405)


@login_required
def registration_datetime_attribute_create(request, registration_pk):
    """API view to create or update a datetime attribute."""
    if request.method == "POST":
        registration = get_object_or_404(Registration, id=registration_pk)
        attribute_module_id = request.POST.get("attribute_module")
        attribute_module = get_object_or_404(AttributeModule, id=attribute_module_id)

        datetime_value = request.POST.get("date_time_field")

        # Try to get existing attribute or create new one
        try:
            attribute = DateTimeAttribute.objects.get(
                attribute_module=attribute_module, registration=registration
            )
            attribute.date_time_field = datetime_value
            attribute.save()
        except DateTimeAttribute.DoesNotExist:
            attribute = DateTimeAttribute.objects.create(
                attribute_module=attribute_module,
                registration=registration,
                date_time_field=datetime_value,
            )

        return JsonResponse(
            {"id": attribute.id, "date_time_field": attribute.date_time_field}
        )
    return JsonResponse({"error": "Only POST method is allowed"}, status=405)


@login_required
def registration_integer_attribute_create(request, registration_pk):
    """API view to create or update an integer attribute."""
    if request.method == "POST":
        registration = get_object_or_404(Registration, id=registration_pk)
        attribute_module_id = request.POST.get("attribute_module")
        attribute_module = get_object_or_404(AttributeModule, id=attribute_module_id)

        # Handle empty value
        integer_value = request.POST.get("integer_field")
        if integer_value == "":
            integer_value = 0
        else:
            integer_value = int(integer_value)

        # Try to get existing attribute or create new one
        try:
            attribute = IntegerAttribute.objects.get(
                attribute_module=attribute_module, registration=registration
            )
            attribute.integer_field = integer_value
            attribute.save()
        except IntegerAttribute.DoesNotExist:
            attribute = IntegerAttribute.objects.create(
                attribute_module=attribute_module,
                registration=registration,
                integer_field=integer_value,
            )

        return JsonResponse(
            {"id": attribute.id, "integer_field": attribute.integer_field}
        )
    return JsonResponse({"error": "Only POST method is allowed"}, status=405)


@login_required
def registration_float_attribute_create(request, registration_pk):
    """API view to create or update a float attribute."""
    if request.method == "POST":
        registration = get_object_or_404(Registration, id=registration_pk)
        attribute_module_id = request.POST.get("attribute_module")
        attribute_module = get_object_or_404(AttributeModule, id=attribute_module_id)

        # Handle empty value
        float_value = request.POST.get("float_field")
        if float_value == "":
            float_value = 0.0
        else:
            float_value = float(float_value)

        # Try to get existing attribute or create new one
        try:
            attribute = FloatAttribute.objects.get(
                attribute_module=attribute_module, registration=registration
            )
            attribute.float_field = float_value
            attribute.save()
        except FloatAttribute.DoesNotExist:
            attribute = FloatAttribute.objects.create(
                attribute_module=attribute_module,
                registration=registration,
                float_field=float_value,
            )

        return JsonResponse({"id": attribute.id, "float_field": attribute.float_field})
    return JsonResponse({"error": "Only POST method is allowed"}, status=405)


@login_required
def registration_travel_attribute_create(request, registration_pk):
    """API view to create or update a travel attribute."""
    if request.method == "POST":
        registration = get_object_or_404(Registration, id=registration_pk)
        attribute_module_id = request.POST.get("attribute_module")
        attribute_module = get_object_or_404(AttributeModule, id=attribute_module_id)

        number_persons = int(request.POST.get("number_persons", 0))
        type_field = request.POST.get("type_field", "Train")
        date_time_field = request.POST.get("date_time_field")
        description = request.POST.get("description", "")

        # Try to get existing attribute or create new one
        try:
            attribute = TravelAttribute.objects.get(
                attribute_module=attribute_module, registration=registration
            )
            attribute.number_persons = number_persons
            attribute.type_field = type_field
            attribute.date_time_field = date_time_field
            attribute.description = description
            attribute.save()
        except TravelAttribute.DoesNotExist:
            attribute = TravelAttribute.objects.create(
                attribute_module=attribute_module,
                registration=registration,
                number_persons=number_persons,
                type_field=type_field,
                date_time_field=date_time_field,
                description=description,
            )

        return JsonResponse(
            {
                "id": attribute.id,
                "number_persons": attribute.number_persons,
                "type_field": attribute.type_field,
                "date_time_field": attribute.date_time_field,
                "description": attribute.description,
            }
        )
    return JsonResponse({"error": "Only POST method is allowed"}, status=405)


@login_required
def registration_create(request, event_slug):
    """
    View to create a new registration.
    """
    event = get_object_or_404(Event, slug=event_slug)
    if request.method == "POST":
        form = RegistrationBaseForm(request.POST)
        if form.is_valid():
            registration = form.save(commit=False)
            registration.event = event
            registration.save()
            return redirect("reg-detail-overview", reg_id=registration.id)
    else:
        form = RegistrationBaseForm()

    return render(
        request,
        "registration_create/main.html",
        {
            "form": form,
            "event": event,
        },
    )


@method_decorator(login_required, name="dispatch")
class RegistrationWizardView(SessionWizardView):
    template_name = "registration_create_wizard/generic_step.html"

    def get_form_initial(self, step):
        initial = self.initial_dict.get(step, {})
        # You can pre-populate form fields here if needed
        return initial

    def get_form_kwargs(self, step=None):
        kwargs = super().get_form_kwargs(step)
        if step:
            event_slug = self.kwargs.get("event_slug")
            event = get_object_or_404(Event, slug=event_slug)
            # Get event module for this step
            event_modules = list(
                EventModule.objects.filter(event=event).order_by("ordering")
            )
            step_index = int(step.split('-')[-1]) if '-' in step else int(step)
            if step_index < len(event_modules):
                kwargs["event_module"] = event_modules[step_index]
                # Also pass the event object to the form
                kwargs["event"] = event
        return kwargs

    def get_form_list(self):
        """
        Dynamically create forms for each event module
        """
        event_slug = self.kwargs.get("event_slug")
        event = get_object_or_404(Event, slug=event_slug)
        event_modules = EventModule.objects.filter(event=event).order_by("ordering")

        form_list = {}
        for i, event_module in enumerate(event_modules):

            if event_module.name == "Participants":
                form_list[f"module-{str(i)}"] = ParticipantForm

            elif event_module.name == "ScoutGroup":
                form_list[f"module-{str(i)}"] = ScoutGroupForm
            else:
                # Create a form class for this event module
                form_class = create_module_form_class(event_module)
                form_list[str(i)] = form_class

        return form_list

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        event_slug = self.kwargs.get("event_slug")
        event = get_object_or_404(Event, slug=event_slug)
        event_modules = list(
            EventModule.objects.filter(event=event).order_by("ordering")
        )
        context["event"] = event
        context["event_modules"] = event_modules
        step_index = int(self.steps.current.split('-')[-1]) if '-' in self.steps.current else int(self.steps.current)
        context["event_module"] = event_modules[step_index]
        return context

    def done(self, form_list,form_dict, **kwargs):
        """
        Process the form data when all steps are complete
        """
        event_slug = self.kwargs.get("event_slug")
        event = get_object_or_404(Event, slug=event_slug)
        event_modules = list(EventModule.objects.filter(event=event))

        try:
            scout_group_dict = form_dict['0'].cleaned_data
            scout_group = scout_group_dict.get('scout_group')
        except KeyError:
            scout_group = None

        # Create a registration
        registration = Registration.objects.create(
            event=event,
            scout_organisation=scout_group,
        )
        # Set many-to-many relationship after creation
        registration.responsible_persons.set([self.request.user])

        # Save all form data
        for i, form in enumerate(form_list):
            if i < len(event_modules):
                event_module = event_modules[i]
                form_data = form.cleaned_data

                try:
                    obj = form_dict[str(i)].cleaned_data
                except KeyError:
                    obj = form_dict[f"module-{i}"].cleaned_data

                # Handle the participant creation
                if obj.get('first_name', None):
                    print("Creating participant")
    
                    participant_kwargs = {
                        'registration': registration,
                        'first_name': obj.get('first_name'),
                        'last_name': obj.get('last_name', ''),
                        'scout_name': obj.get('scout_name', ''),
                        'address': obj.get('address', ''),
                        'birthday': obj.get('birthday'),
                        'gender': obj.get('gender', '')
                    }
                    
                    # Add zip_code if it exists
                    if obj.get('zip_code'):
                        try:
                            zip_code_instance = basic_models.ZipCode.objects.get(zip_code=obj.get('zip_code'))
                            participant_kwargs['zip_code'] = zip_code_instance
                        except basic_models.ZipCode.DoesNotExist:
                            pass
                    
                    # Create the participant
                    participant = RegistrationParticipant.objects.create(**participant_kwargs)
                    
                    # Handle many-to-many relationships if present
                    if obj.get('eat_habit'):
                        participant.eat_habit.set(obj.get('eat_habit'))
                    
                    if obj.get('scout_level'):
                        participant.scout_level = obj.get('scout_level')
                        participant.save()

                    # end of participant creation

                for field_name, value in form_data.items():
                    # Extract attribute module ID from field name (e.g., 'attribute_123')
                    if field_name.startswith("attribute_"):
                        attribute_id = int(field_name.split("_")[1])
                        attribute_module = AttributeModule.objects.get(id=attribute_id)

                        # Create or update the attribute based on its type
                        if attribute_module.field_type == "BoA":
                            # Default to False if value is None
                            boolean_value = False if value is None else bool(value)
                            BooleanAttribute.objects.create(
                                registration=registration,
                                attribute_module=attribute_module,
                                boolean_field=boolean_value,
                            )
                        elif attribute_module.field_type == "StA":
                            # Convert to empty string if None
                            string_value = "" if value is None else str(value)
                            StringAttribute.objects.create(
                                registration=registration,
                                attribute_module=attribute_module,
                                string_field=string_value,
                            )
                        elif attribute_module.field_type == "InA":
                            # Default to 0 if None or not convertible to int
                            try:
                                integer_value = 0 if value is None else int(value)
                            except (ValueError, TypeError):
                                integer_value = 0
                            IntegerAttribute.objects.create(
                                registration=registration,
                                attribute_module=attribute_module,
                                integer_field=integer_value,
                            )
                        elif attribute_module.field_type == "FlA":
                            # Default to 0.0 if None or not convertible to float
                            try:
                                float_value = 0.0 if value is None else float(value)
                            except (ValueError, TypeError):
                                float_value = 0.0
                            FloatAttribute.objects.create(
                                registration=registration,
                                attribute_module=attribute_module,
                                float_field=float_value,
                            )
                        elif attribute_module.field_type == "TiA":
                            # Don't provide date_time_field if value is None
                            kwargs = {
                                "registration": registration,
                                "attribute_module": attribute_module,
                            }
                            if value is not None:
                                kwargs["date_time_field"] = value
                            DateTimeAttribute.objects.create(**kwargs)
                        elif attribute_module.field_type == "TrA":
                            # For travel attributes, we expect value to be either a dictionary
                            # or we need to parse it from form data with specific field names
                            if isinstance(value, dict):
                                travel_data = value
                            else:
                                # If it's not a dictionary, use default values
                                travel_data = {
                                    "number_persons": 1,
                                    "type_field": "Train",
                                    "date_time_field": None,
                                    "description": value if value else "",
                                }

                                # Try to get related fields from the form data
                                persons_field = f"attribute_{attribute_id}_persons"
                                type_field = f"attribute_{attribute_id}_type"
                                datetime_field = f"attribute_{attribute_id}_datetime"
                                desc_field = f"attribute_{attribute_id}_description"

                                if persons_field in form_data:
                                    travel_data["number_persons"] = form_data[
                                        persons_field
                                    ]
                                if type_field in form_data:
                                    travel_data["type_field"] = form_data[type_field]
                                if datetime_field in form_data:
                                    travel_data["date_time_field"] = form_data[
                                        datetime_field
                                    ]
                                if desc_field in form_data:
                                    travel_data["description"] = form_data[desc_field]

                            TravelAttribute.objects.create(
                                registration=registration,
                                attribute_module=attribute_module,
                                number_persons=int(
                                    travel_data.get("number_persons", 1)
                                ),
                                type_field=travel_data.get("type_field", "Train"),
                                date_time_field=travel_data.get("date_time_field"),
                                description=travel_data.get("description", ""),
                            )
        # Redirect to the registration overview page
        messages.success(self.request, "Anmeldung erfolgreich abgeschlossen!")
        return redirect(
            reverse("registration-final", kwargs={"reg_id": registration.id})
        )


@login_required
def registration_final(request, reg_id):
    """
    View for the final step of the registration process.
    """
    registration = get_object_or_404(Registration, id=reg_id)
    event = registration.event

    return render(
        request,
        "registration_create_wizard/final.html",
        {
            "event": event,
            "reg": registration,
            "breadcrumbs": [
                {"name": "Alle Veranstaltungen", "url": reverse("event-list")},
                {
                    "name": event.name,
                    "url": reverse("event-detail-overview", args=[event.slug]),
                },
                {
                    "name": "Anmeldung",
                    "url": reverse("reg-detail-overview", args=[registration.id]),
                },
                {"name": "Abschluss", "url": "#"},
            ],
        },
    )


@login_required
def send_confirmation_email(request, reg_id):
    """
    View for resending confirmation emails for a registration.
    """
    registration = get_object_or_404(Registration, id=reg_id)

    event_email_send_confirmation(
        request, registration=registration, event=registration.event
    )
    messages.success(request, "Die Bestätigungs-E-Mail wurde erneut versendet!")

    # Redirect back to the manage page
    return redirect("reg-detail-manage", reg_id=registration.id)


@login_required
def registration_revoke(request, reg_id):
    """
    View for revoking (soft deleting) a registration.
    """
    registration = get_object_or_404(Registration, id=reg_id)
    event = registration.event

    # Check if the current user has permission to revoke this registration
    if (
        not request.user.is_superuser
        and request.user not in registration.responsible_persons.all()
    ):
        messages.error(
            request, "Du hast keine Berechtigung, diese Anmeldung zu widerrufen."
        )
        return redirect("reg-detail-manage", reg_id=reg_id)

    if request.method == "POST":
        form = RegistrationRevocationForm(request.POST)
        if form.is_valid():
            if form.cleaned_data.get("confirm"):
                # Soft delete by setting deleted_at timestamp
                registration.deleted_at = timezone.now()
                registration.deleted_reason = form.cleaned_data.get("reason")
                registration.deleted_by = request.user
                registration.save()

                messages.success(request, "Die Anmeldung wurde erfolgreich widerrufen.")
                return redirect("event-detail-overview", slug=event.slug)
    else:
        form = RegistrationRevocationForm()

    return render(
        request,
        "registration_revoke/main.html",
        {
            "event": event,
            "reg": registration,
            "form": form,
            "breadcrumbs": [
                {"name": "Alle Veranstaltungen", "url": reverse("event-list")},
                {
                    "name": event.name,
                    "url": reverse("event-detail-overview", args=[event.slug]),
                },
                {
                    "name": "Anmeldung",
                    "url": reverse("reg-detail-overview", args=[registration.id]),
                },
                {
                    "name": "Verwaltung",
                    "url": reverse("reg-detail-manage", args=[registration.id]),
                },
                {"name": "Anmeldung widerrufen", "url": "#"},
            ],
        },
    )

@login_required
def download_registrations(request, reg_id):
    """
    View to download registrations in CSV format.
    """
    registration = get_object_or_404(Registration, id=reg_id)
    event = registration.event
    
    # Check permissions
    if not request.user.is_superuser and request.user not in registration.responsible_persons.all():
        messages.error(request, "Du hast keine Berechtigung, diese Daten herunterzuladen.")
        return redirect("reg-detail-overview", reg_id=reg_id)
    
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{event.name}_registrations.csv"'
    
    writer = csv.writer(response)
    # Write header row
    writer.writerow(['ID', 'Scout Organisation', 'Scout Group', 'Responsible Person', 'Created At', 'Status', 'Participants'])
    
    # Write registration data
    writer.writerow([
        registration.id,
        registration.scout_organisation.name if registration.scout_organisation else '',
        registration.scout_group,
        ", ".join([person.scout_display_name for person in registration.responsible_persons.all()]),
        registration.created_at.strftime('%Y-%m-%d %H:%M'),
        registration.get_status_display(),
        registration.participants.count(),
    ])
    
    return response

def download_participants(request, reg_id):
    """
    View to download participants in CSV format.
    """
    registration = get_object_or_404(Registration, id=reg_id)
    event = registration.event
    
    # Check permissions
    if not request.user.is_superuser and request.user not in registration.responsible_persons.all():
        messages.error(request, "Du hast keine Berechtigung, diese Daten herunterzuladen.")
        return redirect("reg-detail-overview", reg_id=reg_id)
    
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{event.name}_participants.csv"'
    
    writer = csv.writer(response)
    # Write header row
    writer.writerow(['ID', 'First Name', 'Last Name', 'Scout Name', 'Birthday', 'Gender', 
                     'Address', 'ZIP Code', 'City', 'Eating Habits', 'Scout Level'])
    
    # Write participant data for each participant
    for participant in registration.participants.all():
        writer.writerow([
            participant.id,
            participant.first_name,
            participant.last_name,
            participant.scout_name or '',
            participant.birthday.strftime('%Y-%m-%d') if participant.birthday else '',
            participant.get_gender_display(),
            participant.address,
            participant.zip_code.zip_code if participant.zip_code else '',
            participant.zip_code.city if participant.zip_code else '',
            ', '.join([habit.name for habit in participant.eat_habit.all()]),
            participant.scout_level.name if participant.scout_level else '',
        ])
    
    return response


@login_required
def download_invoice(request, reg_id):
    """
    View to generate and download an invoice for a registration.
    """
    registration = get_object_or_404(Registration, id=reg_id)
    event = registration.event
    
    # Check permissions
    if not request.user.is_superuser and request.user not in registration.responsible_persons.all():
        messages.error(request, "Du hast keine Berechtigung, diese Rechnung herunterzuladen.")
        return redirect("reg-detail-overview", reg_id=reg_id)
    
    
    # Create a file-like buffer to receive PDF data
    buffer = BytesIO()
    
    # Create the PDF object, using the buffer as its "file"
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    subtitle_style = styles['Heading2']
    normal_style = styles['Normal']
    
    # Add title
    elements.append(Paragraph(f"Rechnung - {event.name}", title_style))
    elements.append(Spacer(1, 0.5*inch))
    
    # Add registration details
    elements.append(Paragraph("Anmeldeinformationen:", subtitle_style))
    elements.append(Paragraph(f"Anmeldung ID: {registration.id}", normal_style))
    elements.append(Paragraph(f"Organisation: {registration.scout_organisation.name if registration.scout_organisation else 'N/A'}", normal_style))
    elements.append(Paragraph(f"Erstellt am: {registration.created_at.strftime('%d.%m.%Y')}", normal_style))
    
    # Add spacer
    elements.append(Spacer(1, 0.5*inch))
    
    # Add participant information
    elements.append(Paragraph("Teilnehmende:", subtitle_style))
    
    # Create participant table
    participant_data = [['Name', 'Scout Name', 'Alter', 'Geschlecht']]
    
    for p in registration.participants.all():
        # Calculate age if birthday is available
        age = ""
        if p.birthday:
            today = date.today()
            age = today.year - p.birthday.year - ((today.month, today.day) < (p.birthday.month, p.birthday.day))
            age = str(age)
            
        participant_data.append([
            f"{p.first_name} {p.last_name}",
            p.scout_name or "",
            age,
            p.get_gender_display()
        ])
    
    # Create the table
    if len(participant_data) > 1:  # Only if we have participants
        participant_table = Table(participant_data, colWidths=[2*inch, 1.5*inch, 0.75*inch, 1.25*inch])
        participant_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(participant_table)
    else:
        elements.append(Paragraph("Keine Teilnehmer vorhanden.", normal_style))
    
    elements.append(Spacer(1, 0.5*inch))
    
    # Cost calculation
    participant_count = registration.participants.count()
    cost_per_participant = 0
    total_cost = participant_count * cost_per_participant
    
    # Add cost information
    elements.append(Paragraph("Kostenübersicht:", subtitle_style))
    
    cost_data = [
        ['Beschreibung', 'Anzahl', 'Preis pro Person', 'Gesamtpreis'],
        ['Teilnahmegebühr', str(participant_count), f"{cost_per_participant} €", f"{total_cost} €"]
    ]
    
    cost_table = Table(cost_data, colWidths=[2.5*inch, 1*inch, 1.5*inch, 1.5*inch])
    cost_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(cost_table)
    
    elements.append(Spacer(1, 0.25*inch))
    elements.append(Paragraph(f"Gesamtbetrag: {total_cost} €", ParagraphStyle('Total', 
                                                                fontSize=14, 
                                                                alignment=2, 
                                                                fontName='Helvetica-Bold')))
    
    # Add payment information
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph("Zahlungsinformationen:", subtitle_style))
    elements.append(Paragraph(f"Bitte überweisen Sie den Gesamtbetrag bis zum {(event.registration_deadline or event.start_date).strftime('%d.%m.%Y') if (event.registration_deadline or event.start_date) else 'Veranstaltungsbeginn'} auf folgendes Konto:", normal_style))
    
    # Example bank details - these should be replaced with actual values from settings or event data
    elements.append(Paragraph("Kontoinhaber: Scout Organization", normal_style))
    elements.append(Paragraph("IBAN: DE12 3456 7890 1234 5678 90", normal_style))
    elements.append(Paragraph("BIC: ABCDEFGHIJK", normal_style))
    elements.append(Paragraph(f"Verwendungszweck: {event.name} - Anmeldung {registration.id}", normal_style))
    
    # Build the PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer
    pdf = buffer.getvalue()
    buffer.close()
    
    # Create the HTTP response with PDF mime type
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="rechnung_{event.name}_{registration.id}.pdf"'
    
    # Write the PDF to the response
    response.write(pdf)
    
    return response


