from copy import deepcopy
from .models import (
    Event,
    EventPermission,
    BookingOption,
    EventModule,
    StandardEventTemplate,
)
from anmelde_tool.registration.models import Registration
from anmelde_tool.attributes.models import AttributeModule
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.utils.text import slugify
from django import forms
from formtools.wizard.views import SessionWizardView, CookieWizardView
from anmelde_tool.attributes.forms import GeneralAttributeForm
from anmelde_tool.attributes.models import AttributeModule, AttributeChoiceOption
from masterdata.models import ZipCode, EventLocation
from django.utils import timezone
from datetime import datetime

from .forms import (
    EventCreateForm,
    EventPermissionFormSet,
    EventPermissionCreateForm,
    BookingOptionForm,
    EventFormModelForm,
    EventListFilter,
    EventPermissionFilter,
    EventRegistrationSearchFilterForm,
    EventModuleSearchFilterForm,
    ListAttributeForm,
)

from .models import StandardEventTemplate


def add_event_attribute(
    attribute_module: AttributeModule, event_module: EventModule
) -> AttributeModule:
    new_attribute_module: AttributeModule = deepcopy(attribute_module)
    new_attribute_module.pk = None
    new_attribute_module.id = None
    new_attribute_module.standard = False
    new_attribute_module.event_module = event_module
    new_attribute_module.save()
    return new_attribute_module


def add_event_module(module: EventModule, event: Event) -> EventModule:
    new_module: EventModule = deepcopy(module)
    new_module.pk = None
    new_module.standard = False
    new_module.event = event
    new_module.save()
    for attribute_module in module.attributemodule_set.all():
        add_event_attribute(attribute_module, new_module)
    return new_module


EVENT_WIZARD_TEMPLATES = {
    "intro": "event_create_wizard/0-intro-step.html",
    "basic_info": "event_create_wizard/generic_step.html",
    "location": "event_create_wizard/generic_step.html",
    "location_create": "event_create_wizard/generic_step.html",
    "schedule": "event_create_wizard/generic_step.html",
    "invite": "event_create_wizard/invite_step.html",
    "booking_option": "event_create_wizard/generic_step.html",
    "module": "event_create_wizard/generic_step.html",
    "permission": "event_create_wizard/generic_step.html",
    "registration_type": "event_create_wizard/generic_step.html",
    "summary": "event_create_wizard/generic_step.html",
}


class EventWizardView(SessionWizardView):
    """
    A wizard view for creating an event step by step.
    """

    condition_dict = {
        "location_create": lambda wizard: wizard.get_cleaned_data_for_step("location")
        and wizard.get_cleaned_data_for_step("location").get("add_new_location", False)
        is True
    }

    def get_template_names(self):
        """Return the template for the current step."""
        return [EVENT_WIZARD_TEMPLATES[self.steps.current]]

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        context["step_title"] = self.get_step_title(self.steps.current)
        context["step_description"] = self.get_step_description(self.steps.current)
        context["total_steps"] = len(self.form_list)

        # Add step titles for all steps to be used in the template
        step_titles = {}
        for step in self.steps.all:
            step_titles[step] = self.get_step_title(step)
        context["step_titles"] = step_titles

        # Add specific context for invite step (formset)
        if self.steps.current == "invite":
            # Make sure we pass the management form
            if hasattr(form, "management_form"):
                context["management_form"] = form.management_form
            context["forms"] = form

        return context

    def get_form(self, step=None, data=None, files=None):
        form = super().get_form(step, data, files)

        # Initialize the formset with previous data if available
        if step == "invite" and not data:
            participant_data = self.storage.get_step_data("invite")
            if participant_data:
                form = EventPermissionFormSet(initial=self.get_invite_initial_data())
                # Ensure the management form is properly initialized
                form.management_form.initial["TOTAL_FORMS"] = len(
                    self.get_invite_initial_data()
                )
                form.management_form.initial["INITIAL_FORMS"] = 0

        if step == "booking_option":
            # Prepopulate the booking option form with event data if available
            schedule_data = self.storage.get_step_data("schedule")
            if schedule_data:
                # Extract the schedule data from the storage
                try:
                    # Get schedule data values
                    start_date = schedule_data.get("schedule-start_date", [""])
                    end_date = schedule_data.get("schedule-end_date", [""])
                    registration_start = schedule_data.get(
                        "schedule-registration_start", [""]
                    )

                    # Set initial values for the booking option form
                    form.initial.update(
                        {
                            "name": "Normal",
                            "description": "Normale Buchung",
                            "price": 20,
                            "start_date": start_date if start_date else None,
                            "end_date": end_date if end_date else None,
                            "bookable_from": (
                                registration_start if registration_start else None
                            ),
                            "bookable_till": start_date if start_date else None,
                            "is_public": True,
                        }
                    )
                except Exception as e:
                    # In case of any error, just continue without pre-populating
                    print(f"Error pre-populating booking option form: {e}")

        return form

    def get_invite_initial_data(self):
        """Get initial data for the invite formset from storage"""
        step_data = self.storage.get_step_data("invite")
        if not step_data:
            return []

        # Extract formset data from storage and convert to initial format
        initial_data = []
        total_forms = int(step_data.get("invite-TOTAL_FORMS", 0))

        for i in range(total_forms):
            prefix = f"invite-{i}-"
            form_data = {
                "user": step_data.get(f"{prefix}user", ""),
                "group": step_data.get(f"{prefix}group", ""),
                "permission_type": step_data.get(f"{prefix}permission_type", ""),
                "include_subgroups": step_data.get(f"{prefix}include_subgroups", "")
                == "on",
            }

            if not form_data["user"] and not form_data["group"]:
                continue

            initial_data.append(form_data)

        return initial_data

    def get_step_title(self, step):
        """Return a title for the current step."""
        titles = {
            "intro": "Willkommen beim Event-Assistenten",
            "basic_info": "Basis Infos",
            "location": "Ort",
            "location_create": "Neuen Veranstaltungsort erstellen",
            "schedule": "Zeitplan",
            "invite": "Einladungen",
            "booking_option": "Buchungsoptionen",
            "module": "Module",
            "permission": "Berechtigungen",
            "registration_type": "Anmeldetyp",
            "summary": "Zusammenfassung",
        }
        return titles.get(step, "Step")

    def get_step_description(self, step):
        """Return a description for the current step."""
        descriptions = {
            "intro": "Erstelle dein Event Schritt für Schritt.",
            "basic_info": "Gib grundlegende Details über das Event an.",
            "location": "Wähle einen Veranstaltungsort aus.",
            "location_create": "Erstelle einen neuen Veranstaltungsort.",
            "schedule": "Lege den Zeitplan des Events fest.",
            "invite": "Wähle aus welche Personen auf das Event eingeladen werden sollen.",
            "booking_option": "Erstelle Buchungsoptionen für dein Event. Weitere Optionen können später hinzugefügt werden.",
            "module": "Wähle Module aus, die für das Event relevant sind.",
            "permission": "Definiere Berechtigungen für das Event.",
            "registration_type": "Wähle den Anmeldetyp für das Event aus.",
            "summary": "Überprüfe und finalisiere dein Event.",
        }
        return descriptions.get(step, "")

    def done(self, form_list, form_dict, **kwargs):
        """Process the forms and create the event."""

        # Extract form data
        basic_info = form_dict["basic_info"].cleaned_data
        location_data = form_dict["location"].cleaned_data
        schedule = form_dict["schedule"].cleaned_data
        registration_type = form_dict["registration_type"].cleaned_data

        # Get or create location
        location = None
        if (
            location_data.get("add_new_location") is True
            and "location_create" in form_dict
        ):
            # User wants to create a new location
            location_create_data = form_dict["location_create"].cleaned_data

            zip_code = location_create_data.get("zip_code", "")

            zip_code_instance = ZipCode.objects.filter(zip_code=zip_code).first()

            location = EventLocation.objects.create(
                name=location_create_data.get("name"),
                address=location_create_data.get("street", ""),
                zip_code=zip_code_instance,
            )
        else:
            # User selected an existing location
            location = location_data.get("location")

        slug = slugify(basic_info.get("name"))[:20]

        if Event.objects.filter(slug=slug).exists():
            slug += "-" + str(Event.objects.filter(slug=slug).count() + 1)

        name = basic_info.get("name")

        if Event.objects.filter(name=name).exists():
            name += "-" + str(Event.objects.filter(name=name).count() + 1)

        # Create the event
        event = Event.objects.create(
            name=name,
            slug=slug,
            short_description=basic_info.get("short_description", ""),
            long_description=basic_info.get("long_description", ""),
            location=location,
            start_date=schedule.get("start_date"),
            end_date=schedule.get("end_date"),
            registration_start=schedule.get("registration_start"),
            registration_deadline=schedule.get("registration_deadline"),
            last_possible_update=schedule.get("last_possible_update"),
            is_public=basic_info.get("is_public", False),
            created_by=self.request.user,
            registration_type=registration_type.get("event_registration_type", ""),
        )

        # Create booking option
        booking_option = form_dict["booking_option"]
        if booking_option:
            BookingOption.objects.create(
                name=booking_option.cleaned_data.get("name"),
                description=booking_option.cleaned_data.get("description", ""),
                price=booking_option.cleaned_data.get("price", 0),
                max_participants=booking_option.cleaned_data.get("max_participants", 0),
                bookable_from=booking_option.cleaned_data.get("bookable_from"),
                bookable_till=booking_option.cleaned_data.get("bookable_till"),
                start_date=booking_option.cleaned_data.get("start_date"),
                end_date=booking_option.cleaned_data.get("end_date"),
                is_public=booking_option.cleaned_data.get("is_public", False),
                event=event,
                created_by=self.request.user,
            )

        modules = form_dict["module"].cleaned_data.get("modules", [])
        if modules:
            for module in modules:
                event_module = EventModule.objects.get(id=module.id)
                new_module = add_event_module(event_module, event)
                new_module.save()

        standard_modules = EventModule.objects.filter(id__in=[14, 13, 16, 17, 15])
        for module in standard_modules:
            new_module = add_event_module(module, event)
            new_module.save()

        # Create event permission for the creator with full rights
        EventPermission.objects.create(
            event=event,
            user=self.request.user,
            permission_type="edit",
            created_by=self.request.user,
        )

        # Process the invite step data to create permissions
        if "invite" in form_dict and form_dict["invite"]:
            invite_data = form_dict["invite"].cleaned_data
            print("invite_data")
            print(invite_data)
            if hasattr(invite_data, "cleaned_data") and hasattr(
                invite_data, "is_valid"
            ):
                # If it's a single form
                if invite_data.get("user") or invite_data.get("group"):
                    EventPermission.objects.create(
                        event=event,
                        user=invite_data.get("user"),
                        group=invite_data.get("group"),
                        permission_type=invite_data.get("permission_type", "invite"),
                        include_subgroups=invite_data.get("include_subgroups", False),
                        created_by=self.request.user,
                    )
            elif hasattr(invite_data, "forms"):
                # If it's a formset
                for form in invite_data.forms:
                    if form.is_valid() and (form.get("user") or form.get("group")):
                        EventPermission.objects.create(
                            event=event,
                            user=form.get("user"),
                            group=form.get("group"),
                            permission_type=form.get("permission_type", "invite"),
                            include_subgroups=form.get("include_subgroups", False),
                            created_by=self.request.user,
                        )

        return HttpResponseRedirect(reverse("event-wizard-final", args=[event.slug]))


@login_required
def event_list(request):
    """
    View for listing events with filtering options.
    """
    if not request.GET:
        request.GET = request.GET.copy()
        request.GET["is_future"] = "True"

    search_filter_form = EventListFilter(request.GET)
    events = Event.objects.all()

    if search_filter_form.is_valid():
        events = events.filter(
            name__icontains=search_filter_form.cleaned_data.get("search", "")
        )

        if search_filter_form.cleaned_data.get("is_cancelled"):
            events = events.filter(is_cancelled=True)
        if search_filter_form.cleaned_data.get("is_future"):
            # events = events.filter(is_future=False)
            pass

    if search_filter_form.cleaned_data.get("is_public"):
        events = events.filter(is_public=True)

    paginator = Paginator(events, 10)  # Show 10 events per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    form = EventListFilter(request.GET)
    return render(
        request,
        "event_list/main.html",
        {
            "page_obj": page_obj,
            "form": form,
        },
    )


@login_required
def event_detail_overview(request, slug):
    """
    View for displaying event details.
    """
    event = Event.objects.get(slug=slug)

    # Check if the current user has already registered for this event
    has_already_a_registration = False
    registration = Registration.objects.filter(
        event=event, responsible_persons=request.user, deleted_at__isnull=True
    ).first()

    if registration:
        has_already_a_registration = True
    return render(
        request,
        "event_detail/overview/main.html",
        {
            "event": event,
            "has_already_a_registration": has_already_a_registration,
            "breadcrumbs": [
                {"name": "Veranstaltung", "url": reverse("event-list")},
                {
                    "name": event.name,
                    "url": reverse("event-detail-overview", args=[slug]),
                },
                {
                    "name": "Übersicht",
                },
            ],
        },
    )


@login_required
def event_detail_permission(request, slug):
    """
    View for managing event permissions.
    """
    event = get_object_or_404(Event, slug=slug)
    event_permissions = EventPermission.objects.filter(event=event).order_by(
        "-created_at"
    )

    # Pagination for event permissions
    paginator = Paginator(event_permissions, 10)  # Show 10 permissions per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    search_filter_form = EventPermissionFilter(request.GET)

    # Filter event permissions based on form data
    if search_filter_form.is_valid():
        search_term = search_filter_form.cleaned_data.get("search", "")
        permission_type = search_filter_form.cleaned_data.get("permission_type", "")

        # Apply search filter if provided
        if search_term:
            event_permissions = event_permissions.filter(
                # Search in user's username or group name
                Q(user__username__icontains=search_term)
                | Q(user__first_name__icontains=search_term)
                | Q(user__last_name__icontains=search_term)
                | Q(group__name__icontains=search_term)
            )

        # Apply permission type filter if selected
        if permission_type:
            event_permissions = event_permissions.filter(
                permission_type=permission_type
            )

    # Paginate the filtered results
    paginator = Paginator(event_permissions, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Add permissions page to context
    context = {
        "event": event,
        "page_obj": page_obj,
        "form": search_filter_form,
        "breadcrumbs": [
            {"name": "Veranstaltung", "url": reverse("event-list")},
            {"name": event.name, "url": reverse("event-detail-overview", args=[slug])},
            {"name": "Berechtigungen", "url": "#"},
        ],
    }

    return render(
        request,
        "event_detail/permission/main.html",
        context,
    )


@login_required
def event_detail_module(request, slug):
    """
    View for managing event modules.
    """
    event = get_object_or_404(Event, slug=slug)

    modules = EventModule.objects.filter(event=event).order_by("ordering")

    return render(
        request,
        "event_detail/module/main.html",
        {
            "event": event,
            "modules": modules,
            "breadcrumbs": [
                {"name": "Veranstaltung", "url": reverse("event-list")},
                {
                    "name": event.name,
                    "url": reverse("event-detail-overview", args=[slug]),
                },
                {"name": "Module", "url": "#"},
            ],
        },
    )


@login_required
def event_detail_booking_type(request, slug):
    """
    View for managing event booking types.
    """
    event = get_object_or_404(Event, slug=slug)
    booking_options = BookingOption.objects.filter(event=event)

    return render(
        request,
        "event_detail/booking_type/main.html",
        {
            "event": event,
            "booking_options": booking_options,
            "breadcrumbs": [
                {"name": "Veranstaltung", "url": reverse("event-list")},
                {
                    "name": event.name,
                    "url": reverse("event-detail-overview", args=[slug]),
                },
                {"name": "Buchungsoptionen", "url": "#"},
            ],
        },
    )


@login_required
def event_detail_registration(request, slug):
    """
    View for managing event registrations.
    """
    event = get_object_or_404(Event, slug=slug)

    registrations = event.registrations.all()

    form = EventRegistrationSearchFilterForm(request.GET)

    # Apply filters if form is valid
    if form.is_valid() and form.cleaned_data.get("search"):
        search_term = form.cleaned_data.get("search", "")
        # Search in registration participants
        registrations = (
            registrations.filter(
                participants__first_name__icontains=search_term
            ).distinct()
            | registrations.filter(
                participants__last_name__icontains=search_term
            ).distinct()
            | registrations.filter(
                participants__scout_name__icontains=search_term
            ).distinct()
        )

    # Pagination for registrations
    paginator = Paginator(registrations, 10)  # Show 10 registrations per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "event_detail/registration/main.html",
        {
            "event": event,
            "page_obj": page_obj,
            "form": form,
            "breadcrumbs": [
                {"name": "Veranstaltung", "url": reverse("event-list")},
                {
                    "name": event.name,
                    "url": reverse("event-detail-overview", args=[slug]),
                },
                {"name": "Anmeldungen", "url": "#"},
            ],
        },
    )


@login_required
def event_detail_download(request, slug):
    """
    View for managing event downloads.
    """
    event = get_object_or_404(Event, slug=slug)

    return render(
        request,
        "event_detail/download/main.html",
        {
            "event": event,
            "downloads": [],
            "breadcrumbs": [
                {"name": "Veranstaltung", "url": reverse("event-list")},
                {
                    "name": event.name,
                    "url": reverse("event-detail-overview", args=[slug]),
                },
                {"name": "Downloads", "url": "#"},
            ],
        },
    )


@login_required
def event_detail_invitees(request, slug):
    """
    View for displaying who is invited to the event.
    """
    event = get_object_or_404(Event, slug=slug)

    # Get all event permissions - these represent the invitations
    invitees = EventPermission.objects.filter(event=event).order_by("-created_at")

    # Pagination for invitees
    paginator = Paginator(invitees, 10)  # Show 10 invitees per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "event_detail/invitees/main.html",
        {
            "event": event,
            "page_obj": page_obj,
            "breadcrumbs": [
                {"name": "Veranstaltung", "url": reverse("event-list")},
                {
                    "name": event.name,
                    "url": reverse("event-detail-overview", args=[slug]),
                },
                {"name": "Eingeladene", "url": "#"},
            ],
        },
    )


@login_required
def event_dashboard(request):
    """
    View for displaying an event dashboard with overview statistics.
    """

    # Get permissions for events where user has responsibilities
    permissions = EventPermission.objects.filter(user=request.user).exclude(
        permission_type="invite"
    )

    # Get distinct events based on these permissions
    responsible_events = (
        Event.objects.filter(event_permissions__in=permissions).distinct().count()
    )
    all_future_events = (
        Event.objects.filter(start_date__gte=timezone.now())
        .order_by("start_date")
        .distinct()
        .count()
    )

    my_events = (
        Event.objects.filter(event_permissions__user=request.user)
        .order_by("start_date")
        .distinct()
        .count()
    )

    my_registrations = (
        Registration.objects.filter(
            responsible_persons__id=request.user.id,
            event__start_date__gte=timezone.now(),
        )
        .order_by("event__start_date")
        .distinct()
        .count()
    )

    return render(
        request,
        "event_dashboard/main.html",
        {
            "responsible_events": responsible_events,
            "all_future_events": all_future_events,
            "my_events": my_events,
            "my_registrations": my_registrations,
        },
    )


@login_required
def event_create(request):
    if request.method == "POST":
        form = EventCreateForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            return redirect("event-detail-overview", pk=event.pk)
    else:
        form = EventCreateForm()
    return render(request, "event_create/main.html", {"form": form})


@login_required
def event_update(request, slug):
    """
    View for updating an existing event.
    """
    event = get_object_or_404(Event, slug=slug)

    if request.method == "POST":
        form = EventCreateForm(request.POST, instance=event)
        if form.is_valid():
            updated_event = form.save(commit=False)
            updated_event.updated_by = request.user
            updated_event.save()
            return redirect("event-detail-overview", slug=event.slug)
    else:
        form = EventCreateForm(instance=event)

    return render(
        request,
        "event_update/main.html",
        {
            "form": form,
            "event": event,
            "breadcrumbs": [
                {"name": "Veranstaltung", "url": reverse("event-list")},
                {
                    "name": event.name,
                    "url": reverse("event-detail-overview", args=[slug]),
                },
                {"name": "Bearbeiten", "url": "#"},
            ],
        },
    )


@login_required
def event_delete(request, slug):
    """
    View to delete an existing event.
    """
    event = get_object_or_404(Event, slug=slug)

    # Check if there are any registrations for this event
    registration_count = event.registrations.count()
    if registration_count > 0:
        error_message = f"Löschen nicht möglich. Es gibt {registration_count} Anmeldung(en) für diese Veranstaltung."
        return render(
            request,
            "event_delete/main.html",
            {
                "event": event,
                "error_message": error_message,
                "has_registrations": True,
                "breadcrumbs": [
                    {"name": "Veranstaltung", "url": reverse("event-list")},
                    {
                        "name": event.name,
                        "url": reverse("event-detail-overview", args=[slug]),
                    },
                    {"name": "Löschen", "url": "#"},
                ],
            },
        )

    if request.method == "POST":
        event.delete()
        return redirect("event-list")

    return render(
        request,
        "event_delete/main.html",
        {
            "event": event,
            "has_registrations": False,
            "breadcrumbs": [
                {"name": "Veranstaltung", "url": reverse("event-list")},
                {
                    "name": event.name,
                    "url": reverse("event-detail-overview", args=[slug]),
                },
                {"name": "Löschen", "url": "#"},
            ],
        },
    )


@login_required
def event_wizard_final(request, slug):
    """Final page after successful event creation."""
    event = get_object_or_404(Event, slug=slug)

    context = {
        "event": event,
    }
    return render(request, "event_create_wizard/final.html", context)


@login_required
def event_permission_create(request, slug):
    """
    View to create permissions for an event.
    """
    event = get_object_or_404(Event, slug=slug)

    if request.method == "POST":
        form = EventPermissionCreateForm(request.POST)
        if form.is_valid():
            permission = form.save(commit=False)
            permission.event = event
            permission.created_by = request.user
            permission.save()
            return redirect("event-detail-permission", slug=slug)
    else:
        form = EventPermissionCreateForm()
    return render(
        request,
        "event_permission/create/main.html",
        {
            "form": form,
            "event": event,
        },
    )


@login_required
def event_permission_update(request, pk):
    """
    View to update an existing permission for an event.
    """
    permission = get_object_or_404(EventPermission, pk=pk)
    event = permission.event

    if request.method == "POST":
        form = EventPermissionCreateForm(request.POST, instance=permission)
        if form.is_valid():
            updated_permission = form.save(commit=False)
            updated_permission.updated_by = request.user
            updated_permission.save()
            return redirect("event-permission-detail", pk=pk)
    else:
        form = EventPermissionCreateForm(instance=permission)

    return render(
        request,
        "event_permission/update/main.html",
        {
            "form": form,
            "event": event,
            "permission": permission,
        },
    )


@login_required
def event_permission_detail(request, pk):
    """
    View for displaying details of a specific event permission.
    """
    permission = get_object_or_404(EventPermission, pk=pk)

    context = {
        "permission": permission,
        "event": permission.event,
        "breadcrumbs": [
            {"name": "Veranstaltung", "url": reverse("event-list")},
            {
                "name": permission.event.name,
                "url": reverse("event-detail-overview", args=[permission.event.slug]),
            },
            {
                "name": "Berechtigungen",
                "url": reverse("event-detail-permission", args=[permission.event.slug]),
            },
        ],
    }

    # Add either user or group to breadcrumbs based on which one is set
    if permission.user:
        context["breadcrumbs"].append({"name": permission.user.username, "url": "#"})
    elif permission.group:
        context["breadcrumbs"].append({"name": permission.group.name, "url": "#"})

    return render(
        request,
        "event_permission/detail/main.html",
        context,
    )


@login_required
def event_permission_delete(request, pk):
    """
    View to delete an existing permission for an event.
    """
    permission = get_object_or_404(EventPermission, pk=pk)
    event = permission.event
    slug = event.slug

    if request.method == "POST":
        permission.delete()
        return redirect("event-detail-permission", slug=slug)

    return render(
        request,
        "event_permission/delete/main.html",
        {
            "permission": permission,
            "event": event,
        },
    )


@login_required
def event_booking_type_create(request, slug):
    """
    View to create a new booking option for an event.
    """
    event = get_object_or_404(Event, slug=slug)

    if request.method == "POST":
        form = BookingOptionForm(data=request.POST)
        if form.is_valid():
            booking_option = form.save(commit=False)
            booking_option.event = event
            booking_option.created_by = request.user
            booking_option.save()
            return redirect("event-detail-booking-type", slug=slug)
    else:
        # Pre-populate form with event data
        initial_data = {
            "start_date": event.start_date,
            "end_date": event.end_date,
            "bookable_from": event.registration_start,
            "bookable_till": event.end_date,
        }
        form = BookingOptionForm(initial=initial_data)

    return render(
        request,
        "event_booking_type/create/main.html",
        {
            "form": form,
            "event": event,
        },
    )


@login_required
def event_booking_type_update(request, pk):
    """
    View to update an existing booking option.
    """
    booking_option = get_object_or_404(BookingOption, pk=pk)
    event = booking_option.event
    slug = event.slug

    if request.method == "POST":
        form = BookingOptionForm(data=request.POST, initial=booking_option.__dict__)
        # Pre-populate form with event data
        if form.is_valid():
            # Update booking option with form data
            for field, value in form.cleaned_data.items():
                setattr(booking_option, field, value)
            booking_option.updated_by = request.user
            booking_option.save()
            return redirect("event-detail-booking-type", slug=slug)
    else:
        form = BookingOptionForm(initial=booking_option.__dict__)

    return render(
        request,
        "event_booking_type/update/main.html",
        {
            "form": form,
            "event": event,
            "booking_option": booking_option,
        },
    )


@login_required
def event_booking_type_delete(request, pk):
    """
    View to delete an existing booking option.
    """
    booking_option = get_object_or_404(BookingOption, pk=pk)
    event = booking_option.event
    slug = event.slug

    if request.method == "POST":
        booking_option.delete()
        return redirect("event-detail-booking-type", slug=slug)

    return render(
        request,
        "event_booking_type/delete/main.html",
        {
            "booking_option": booking_option,
            "event": event,
        },
    )


@login_required
def event_booking_type_detail(request, pk):
    """
    View for displaying details of a specific booking option.
    """
    booking_option = get_object_or_404(BookingOption, pk=pk)
    event = booking_option.event

    return render(
        request,
        "event_booking_type/detail/main.html",
        {
            "booking_option": booking_option,
            "event": event,
            "breadcrumbs": [
                {"name": "Veranstaltung", "url": reverse("event-list")},
                {
                    "name": event.name,
                    "url": reverse("event-detail-overview", args=[event.slug]),
                },
                {
                    "name": "Buchungsoptionen",
                    "url": reverse("event-detail-booking-type", args=[event.slug]),
                },
                {"name": booking_option.name, "url": "#"},
            ],
        },
    )


@login_required
def event_module_create(request, event_slug):
    """
    View to create a new module for an event.
    """
    event = get_object_or_404(Event, slug=event_slug)

    if request.method == "POST":
        form = EventFormModelForm(request.POST)
        if form.is_valid():
            module = form.save(commit=False)
            module.event = event
            module.created_by = request.user
            module.ordering = EventModule.objects.filter(event=event).count() + 1
            module.save()
            return redirect("event-detail-module", slug=event_slug)
    else:
        form = EventFormModelForm()

    return render(
        request,
        "event_module/create/main.html",
        {
            "form": form,
            "event": event,
        },
    )


@login_required
def event_module_add(request, event_slug):
    """
    View to add an existing standard module to an event.
    """
    event = get_object_or_404(Event, slug=event_slug)

    existing_module_types = EventModule.objects.filter(event=event)

    # exclude existing modules on event from available modules
    available_modules = EventModule.objects.filter(
        event__isnull=True, standard=True
    ).exclude(pk__in=existing_module_types.values_list("pk", flat=True))

    existing_module_types = EventModule.objects.filter(event=event)

    # remove existing modules from available modules by name
    available_modules = available_modules.exclude(
        name__in=existing_module_types.values_list("name", flat=True)
    )

    class ModuleSelectForm(forms.Form):
        selected_modules = forms.MultipleChoiceField(
            choices=[(module.pk, module.header) for module in available_modules],
            widget=forms.CheckboxSelectMultiple,
            required=False,
            label="Verfügbare Module",
        )

    if request.method == "POST":
        form = ModuleSelectForm(request.POST)
        if form.is_valid():
            selected_modules = form.cleaned_data.get("selected_modules", [])
            for module_id in selected_modules:
                module = get_object_or_404(EventModule, pk=module_id)
                new_module = add_event_module(module, event)
                new_module.ordering = (
                    EventModule.objects.filter(event=event).count() + 1
                )
                new_module.save()
            return redirect("event-detail-module", slug=event_slug)
    else:
        form = ModuleSelectForm()

    return render(
        request,
        "event_module/add/main.html",
        {
            "event": event,
            "available_modules": available_modules,
            "form": form,
            "breadcrumbs": [
                {"name": "Veranstaltung", "url": reverse("event-list")},
                {
                    "name": event.name,
                    "url": reverse("event-detail-overview", args=[event.slug]),
                },
                {
                    "name": "Module",
                    "url": reverse("event-detail-module", args=[event.slug]),
                },
            ],
        },
    )


@login_required
def event_module_detail(request, pk):
    """
    View for displaying details of a specific event module.
    """
    module = get_object_or_404(EventModule, pk=pk)
    event = module.event
    attributes = AttributeModule.objects.filter(event_module=module)

    return render(
        request,
        "event_module/detail/main.html",
        {
            "module": module,
            "event": event,
            "form": EventModuleSearchFilterForm,
            "attributes": attributes,
            "breadcrumbs": [
                {"name": "Veranstaltung", "url": reverse("event-list")},
                {
                    "name": event.name,
                    "url": reverse("event-detail-overview", args=[event.slug]),
                },
                {
                    "name": "Module",
                    "url": reverse("event-detail-module", args=[event.slug]),
                },
                {"name": module.header, "url": "#"},
            ],
        },
    )


@login_required
def event_module_update(request, pk):
    """
    View to update an existing event module.
    """
    module = get_object_or_404(EventModule, pk=pk)
    event = module.event

    if request.method == "POST":
        form = EventFormModelForm(request.POST, instance=module)
        if form.is_valid():
            updated_module = form.save(commit=False)
            updated_module.save()
            return redirect("event-module-detail", pk=pk)
    else:
        form = EventFormModelForm(instance=module)

    return render(
        request,
        "event_module/update/main.html",
        {
            "form": form,
            "module": module,
            "event": event,
            "breadcrumbs": [
                {"name": "Veranstaltung", "url": reverse("event-list")},
                {
                    "name": event.name,
                    "url": reverse("event-detail-overview", args=[event.slug]),
                },
                {
                    "name": "Module",
                    "url": reverse("event-detail-module", args=[event.slug]),
                },
                {"name": module.header, "url": "#"},
            ],
        },
    )


@login_required
def event_module_delete(request, pk):
    """
    View to delete an existing event module.
    """
    module = get_object_or_404(EventModule, pk=pk)
    event = module.event
    event_slug = event.slug

    if request.method == "POST":
        module.delete()
        # Reorder remaining modules
        remaining_modules = EventModule.objects.filter(event=event).order_by("ordering")
        for i, mod in enumerate(remaining_modules, 1):
            mod.ordering = i
            mod.save()
        return redirect("event-detail-module", slug=event_slug)

    return render(
        request,
        "event_module/delete/main.html",
        {
            "module": module,
            "event": event,
        },
    )


@login_required
def event_module_attribute_create(request, pk):
    """
    View to create a new attribute for an event module.
    """
    module = get_object_or_404(EventModule, pk=pk)
    event = module.event

    if request.method == "POST":
        form = GeneralAttributeForm(request.POST)
        if form.is_valid():
            attribute = form.save(commit=False)
            attribute.event_module = module
            attribute.created_by = request.user
            attribute.save()
            return redirect("event-module-detail", pk=pk)
    else:
        form = GeneralAttributeForm()

    return render(
        request,
        "event_module_attribute/create/main.html",
        {
            "form": form,
            "module": module,
            "event": event,
            "breadcrumbs": [
                {"name": "Veranstaltung", "url": reverse("event-list")},
                {
                    "name": event.name,
                    "url": reverse("event-detail-overview", args=[event.slug]),
                },
                {
                    "name": "Module",
                    "url": reverse("event-detail-module", args=[event.slug]),
                },
                {"name": module.name, "url": "#"},
            ],
        },
    )


@login_required
def event_module_attribute_select_create(request, pk):
    """
    View to create a new attribute for an event module.
    """
    module = get_object_or_404(EventModule, pk=pk)
    event = module.event

    if request.method == "POST":
        form = ListAttributeForm(request.POST)
        if form.is_valid():

            # Get the selected option type
            selected_option = form.cleaned_data.get("attribute")

            # Map the selection to corresponding choices based on type
            if selected_option == "gender":
                choices = [
                    ("male", "Männlich"),
                    ("female", "Weiblich"),
                    ("diverse", "Divers"),
                    ("other", "Sonstiges"),
                ]
                field_type = "RaA"
                title = "Geschlecht"
                text = "Geschlecht"
            elif selected_option == "nutritional_tags":
                choices = [
                    ("vegetarian", "Vegetarisch"),
                    ("vegan", "Vegan"),
                    ("lactose_free", "Laktosefrei"),
                    ("gluten_free", "Glutenfrei"),
                ]
                field_type = "MuA"
                title = "Ernährungsform"
                text = "Ernährungsform"
            elif selected_option == "leader":
                choices = [
                    ("stammesleiter", "Stammesleiter"),
                    ("stammesvorstand", "Stammesvorstand"),
                    ("gruppenleiter", "Gruppenleiter"),
                    ("akela", "Akela"),
                ]
                field_type = "RaA"
                title = "Leiter"
                text = "Leiter"
            elif selected_option == "scout_level":
                choices = [
                    ("woelfling", "Wölfling"),
                    ("jupfi", "Jungpfadfinder"),
                    ("pfadfinder", "Pfadfinder"),
                    ("rover", "Rover"),
                ]
                field_type = "RaA"
                title = "Pfadfinderstufe"
                text = "Pfadfinderstufe"
            elif selected_option == "transportation":
                """"""
                choices = [
                    ("car", "Auto"),
                    ("public_transport", "Öffis"),
                    ("bus", "Reisebus"),
                    ("foot", "Zu Fuß"),
                ]
                field_type = "RaA"
                title = "Transportmittel"
                text = "Transportmittel"
            else:
                choices = []

            attribute_module = AttributeModule.objects.create(
                event_module=module,
                text=text,
                field_type=field_type,
                title=title,
            )

            # Create choice options for the attribute
            for value, label in choices:
                AttributeChoiceOption.objects.create(
                    attribute_module=attribute_module,
                    text=label,
                    ordering=list(choices).index((value, label)) + 1,
                )
                print(f"Created attribute: {label} with value: {value}")

        return redirect("event-module-detail", pk=pk)
    else:
        form = ListAttributeForm()

    return render(
        request,
        "event_module_attribute/create/main.html",
        {
            "form": form,
            "module": module,
            "event": event,
            "breadcrumbs": [
                {"name": "Veranstaltung", "url": reverse("event-list")},
                {
                    "name": event.name,
                    "url": reverse("event-detail-overview", args=[event.slug]),
                },
                {
                    "name": "Module",
                    "url": reverse("event-detail-module", args=[event.slug]),
                },
                {"name": module.name, "url": "#"},
            ],
        },
    )


@login_required
def event_module_attribute_select_create_set(request, pk):
    """
    View to create a new attribute module with predefined attribute settings.
    """
    module = get_object_or_404(EventModule, pk=pk)
    event = module.event

    # Define the attribute settings for each preset type
    ATTRIBUTE_PRESETS = {
        "basic": [
            {"title": "Vorname", "text": "Vorname", "field_type": "StA"},
            {"title": "Nachname", "text": "Nachname", "field_type": "StA"},
            {"title": "Geburtsdatum", "text": "Geburtsdatum", "field_type": "DaA"},
        ],
        "kjp": [
            {"title": "Vorname", "text": "Vorname", "field_type": "StA"},
            {"title": "Nachname", "text": "Nachname", "field_type": "StA"},
            {"title": "Geburtsdatum", "text": "Geburtsdatum", "field_type": "DaA"},
            {"title": "Straße", "text": "Straße", "field_type": "StA"},
            {"title": "PLZ", "text": "PLZ", "field_type": "ZiA"},
            {"title": "Ort", "text": "Ort", "field_type": "StA"},
            {"title": "Bundesland", "text": "Bundesland", "field_type": "StA"},
        ],
        "extended": [
            {"title": "Vorname", "text": "Vorname", "field_type": "StA"},
            {"title": "Nachname", "text": "Nachname", "field_type": "StA"},
            {"title": "Pfadiname", "text": "Pfadiname", "field_type": "StA"},
            {"title": "Geburtsdatum", "text": "Geburtsdatum", "field_type": "DaA"},
            {"title": "Straße", "text": "Straße", "field_type": "StA"},
            {"title": "PLZ", "text": "PLZ", "field_type": "ZiA"},
            {"title": "Ort", "text": "Ort", "field_type": "StA"},
            {"title": "Telefon", "text": "Telefon", "field_type": "PhA"},
            {"title": "Email", "text": "Email", "field_type": "EmA"},
            {"title": "Notfallkontakt", "text": "Notfallkontakt", "field_type": "StA"},
        ],
    }

    class AttributePresetForm(forms.Form):
        PRESET_CHOICES = [
            ("", "-- Bitte wählen --"),
            ("basic", "Basis Attribute"),
            ("kjp", "KJP Attribute"),
            ("extended", "Erweiterte Attribute"),
        ]
        preset = forms.ChoiceField(
            choices=PRESET_CHOICES, required=True, label="Attribut-Vorlage"
        )

    if request.method == "POST":
        form = AttributePresetForm(request.POST)
        if form.is_valid():
            preset_type = form.cleaned_data["preset"]

            # Create attributes based on the selected preset
            if preset_type in ATTRIBUTE_PRESETS:
                attributes = ATTRIBUTE_PRESETS[preset_type]
                for attr in attributes:
                    AttributeModule.objects.create(
                        event_module=module,
                        title=attr["title"],
                        text=attr["text"],
                        ordering=attributes.index(attr) + 1,
                        field_type=attr["field_type"],
                    )

                messages.success(
                    request, f"{len(attributes)} Attribute wurden erstellt."
                )
                return redirect("event-module-detail", pk=pk)
    else:
        form = AttributePresetForm()

    return render(
        request,
        "event_module_attribute/create/main.html",
        {
            "form": form,
            "module": module,
            "event": event,
            "breadcrumbs": [
                {"name": "Veranstaltung", "url": reverse("event-list")},
                {
                    "name": event.name,
                    "url": reverse("event-detail-overview", args=[event.slug]),
                },
                {
                    "name": "Module",
                    "url": reverse("event-detail-module", args=[event.slug]),
                },
                {
                    "name": module.header,
                    "url": reverse("event-module-detail", args=[pk]),
                },
                {"name": "Attribut-Vorlagen", "url": "#"},
            ],
        },
    )


@login_required
def download_registrations(request, event_slug):
    """
    View for downloading all registration data for an event as Excel file.
    """
    event = get_object_or_404(Event, slug=event_slug)

    # Check permissions
    if (
        not request.user.is_superuser
        and not EventPermission.objects.filter(
            event=event, user=request.user, can_edit_event=True
        ).exists()
    ):
        messages.error(
            request, "Du hast keine Berechtigung zum Herunterladen der Anmeldedaten."
        )
        return redirect("event-detail-overview", slug=event.slug)

    # Import necessary libraries
    import pandas as pd
    from django.http import HttpResponse
    from io import BytesIO

    # Get all registrations for this event
    registrations = Registration.objects.filter(event=event)

    # Prepare data for Excel
    data = []
    for reg in registrations:
        # Skip deleted registrations
        if reg.deleted_at:
            continue

        responsible_persons = ", ".join(
            [str(user.scout_display_name) for user in reg.responsible_persons.all()]
        )
        participant_count = reg.participants.count()

        data.append(
            {
                "ID": reg.id,
                "Erstelldatum": reg.created_at,
                "Letzte Änderung": reg.updated_at,
                "Verantwortliche Personen": responsible_persons,
                "Anzahl Teilnehmende": participant_count,
            }
        )

    # Create DataFrame
    df = pd.DataFrame(data)

    # Create Excel file
    output = BytesIO()
    # Convert datetime fields to timezone-naive objects
    for row in data:
        if isinstance(row.get("Erstelldatum"), datetime):
            row["Erstelldatum"] = row["Erstelldatum"].replace(tzinfo=None)
        if isinstance(row.get("Letzte Änderung"), datetime):
            row["Letzte Änderung"] = row["Letzte Änderung"].replace(tzinfo=None)

    # Create DataFrame after datetime conversion
    df = pd.DataFrame(data)

    # Create Excel file
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Anmeldungen", index=False)

    # Prepare response
    output.seek(0)
    response = HttpResponse(
        output.read(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = (
        f'attachment; filename="{event.name}-Anmeldungen.xlsx"'
    )

    messages.success(request, "Die Anmeldedaten wurden erfolgreich heruntergeladen.")

    return response


@login_required
def download_participants(request, event_slug):
    """
    View for downloading all participant data for an event as Excel file.
    """
    event = get_object_or_404(Event, slug=event_slug)

    # Check permissions
    if (
        not request.user.is_superuser
        and not EventPermission.objects.filter(
            event=event, user=request.user, can_edit_event=True
        ).exists()
    ):
        messages.error(
            request, "Du hast keine Berechtigung zum Herunterladen der Teilnehmerdaten."
        )
        return redirect("event-detail-overview", slug=event.slug)

    # Import necessary libraries
    import pandas as pd
    from django.http import HttpResponse
    from io import BytesIO

    # Get all registrations for this event
    registrations = Registration.objects.filter(event=event, deleted_at__isnull=True)

    # Prepare data for Excel
    data = []
    for reg in registrations:
        # Get scout group info if available

        # Get all participants for this registration
        participants = reg.participants.all()

        for participant in participants:
            eat_habits = ", ".join(
                [habit.name for habit in participant.eat_habit.all()]
            )
            data.append(
                {
                    "Anmeldung ID": reg.id,
                    "Vorname": participant.first_name,
                    "Nachname": participant.last_name,
                    "Pfadiname": participant.scout_name,
                    "Geschlecht": participant.get_gender_display(),
                    "Geburtsdatum": participant.birthday,
                    "Alter": participant.age,  # Assuming you have an age property
                    "Adresse": participant.address,
                    "PLZ": (
                        participant.zip_code.zip_code if participant.zip_code else ""
                    ),
                    "Stadt": participant.zip_code.city if participant.zip_code else "",
                    "Ernährungsgewohnheiten": eat_habits,
                }
            )

    # Create DataFrame
    df = pd.DataFrame(data)

    # Create Excel file
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Teilnehmende", index=False)

    # Prepare response
    output.seek(0)
    response = HttpResponse(
        output.read(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = (
        f'attachment; filename="{event.name}-Teilnehmende.xlsx"'
    )

    messages.success(request, "Die Teilnehmerdaten wurden erfolgreich heruntergeladen.")

    return response


@login_required
def download_participants_example(request, event_slug):
    """
    View for downloading an example Excel file for participant data.
    """
    event = get_object_or_404(Event, slug=event_slug)

    # Check permissions
    if (
        not request.user.is_superuser
        and not EventPermission.objects.filter(
            event=event, user=request.user, can_edit_event=True
        ).exists()
    ):
        messages.error(
            request,
            "Du hast keine Berechtigung zum Herunterladen der Beispiel-Teilnehmerdaten.",
        )
        return redirect("event-detail-overview", slug=event.slug)

    # Import necessary libraries
    import pandas as pd
    from django.http import HttpResponse
    from io import BytesIO

    # Prepare example data for Excel
    example_data = [
        {
            "Anmeldung ID": "1",
            "Vorname": "Max",
            "Nachname": "Mustermann",
            "Pfadiname": "PfadiMax",
            "Geschlecht": "Männlich",
            "Geburtsdatum": "2000-01-01",
            "Alter": 23,
            "Adresse": "Musterstraße 1",
            "PLZ": "12345",
            "Stadt": "Musterstadt",
            "Ernährungsgewohnheiten": "Vegetarisch",
        },
        {
            "Anmeldung ID": "2",
            "Vorname": "Erika",
            "Nachname": "Musterfrau",
            "Pfadiname": "PfadiErika",
            "Geschlecht": "Weiblich",
            "Geburtsdatum": "2001-02-02",
            "Alter": 22,
            "Adresse": "Beispielstraße 2",
            "PLZ": "",
            "Stadt": "",
            "Ernährungsgewohnheiten": "",
        },
    ]

    # Create DataFrame
    df = pd.DataFrame(example_data)

    # Create Excel file
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Beispiel-Teilnehmende", index=False)

    # Prepare response
    output.seek(0)
    response = HttpResponse(
        output.read(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = (
        f'attachment; filename="{event.name}-Beispiel-Teilnehmende.xlsx"'
    )
    messages.success(
        request, "Die Beispiel-Teilnehmerdaten wurden erfolgreich heruntergeladen."
    )
    return response
