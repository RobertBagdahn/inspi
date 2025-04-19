from .models import Event, EventLocation, EventPermission, BookingOption, EventModule
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.utils.text import slugify
from formtools.wizard.views import SessionWizardView
from anmelde_tool.attributes.forms import GeneralAttributeForm
from anmelde_tool.attributes.models import AttributeModule

from django.utils import timezone

from .forms import (
    EventCreateForm,
    EventPermissionFormSet,
    EventPermissionCreateForm,
    BookingOptionForm,
    EventFormModelForm,
    EventListFilter,
)

EVENT_WIZARD_TEMPLATES = {
    "intro": "event_create_wizard/0-intro-step.html",
    "basic_info": "event_create_wizard/generic_step.html",
    "location": "event_create_wizard/generic_step.html",
    "schedule": "event_create_wizard/generic_step.html",
    "invite": "event_create_wizard/invite_step.html",
    "summary": "event_create_wizard/generic_step.html",
}


class EventWizardView(SessionWizardView):
    """
    A wizard view for creating an event step by step.
    """

    def get_template_names(self):
        """Return the template for the current step."""
        return [EVENT_WIZARD_TEMPLATES[self.steps.current]]

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        context["step_title"] = self.get_step_title(self.steps.current)
        context["step_description"] = self.get_step_description(self.steps.current)
        context["total_steps"] = len(self.form_list)

        # Add specific context for invite step (formset)
        if self.steps.current == "invite":
            # For formsets, the form passed is actually the formset instance
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
            "intro": "Welcome to the Event Wizard",
            "basic_info": "Basic Information",
            "location": "Event Location",
            "schedule": "Event Schedule",
            "invite": "Einladungen",
            "summary": "Summary",
        }
        return titles.get(step, "Step")

    def get_step_description(self, step):
        """Return a description for the current step."""
        descriptions = {
            "intro": "Create your event step by step.",
            "basic_info": "Provide basic details about the event.",
            "location": "Specify the event location.",
            "schedule": "Set the event schedule.",
            "invite": "Wähle aus welche Personen auf das Event eingeladen werden sollen.",
            "summary": "Review and finalize your event.",
        }
        return descriptions.get(step, "")

    def done(self, form_list, form_dict, **kwargs):
        """Process the forms and create the event."""

        # Extract form data
        basic_info = form_dict["basic_info"].cleaned_data
        location_data = form_dict["location"].cleaned_data
        schedule = form_dict["schedule"].cleaned_data

        slug = slugify(basic_info.get("name"))[:20]

        if Event.objects.filter(slug=slug).exists():
            slug += "-" + str(Event.objects.filter(slug=slug).count() + 1)

        # Create the event
        event = Event.objects.create(
            name=basic_info.get("name"),
            slug=slugify(basic_info.get("name"))[:20],
            short_description=basic_info.get("short_description", ""),
            long_description=basic_info.get("long_description", ""),
            location=location_data.get("location"),
            start_date=schedule.get("start_date"),
            end_date=schedule.get("end_date"),
            registration_start=schedule.get("registration_start"),
            registration_deadline=schedule.get("registration_deadline"),
            last_possible_update=schedule.get("last_possible_update"),
            is_public=basic_info.get("is_public", False),
            created_by=self.request.user,
        )

        # # Add creator as responsible person
        # event.responsible_persons.add(self.request.user)

        return HttpResponseRedirect(reverse(f"event/event-wizard-final/{event.slug}"))


@login_required
def event_list(request):
    """
    View for listing events with filtering options.
    """
    if not request.GET:
        request.GET = request.GET.copy()
        # request.GET['is_not_cancelled'] = 'True'

    search_filter_form = EventListFilter(request.GET)
    events = Event.objects.all()

    if search_filter_form.is_valid():
        events = events.filter(
            name__icontains=search_filter_form.cleaned_data.get("search", "")
        )

        if search_filter_form.cleaned_data.get("is_cancelled"):
            events = events.filter(is_cancelled=True)
        if search_filter_form.cleaned_data.get("is_not_cancelled"):
            events = events.filter(is_cancelled=False)

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

    return render(
        request,
        "event_detail/overview/main.html",
        {
            "event": event,
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
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Add permissions page to context
    context = {
        'event': event,
        'page_obj': page_obj,
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
        },
    )


@login_required
def event_detail_registration(request, slug):
    """
    View for managing event registrations.
    """
    event = get_object_or_404(Event, slug=slug)

    registrations = event.registration_set.all()

    # Pagination for registrations
    paginator = Paginator(registrations, 10)  # Show 10 registrations per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "event_detail/registration/main.html",
        {
            "event": event,
            "page_obj": page_obj,
        },
    )


@login_required
def event_dashboard(request):
    """
    View for displaying an event dashboard with overview statistics.
    """
    # Get events for the current user
    # responsible_events = Event.objects.filter(responsible_persons=request.user)

    # # Get all public events
    # public_events = Event.objects.filter(is_public=True)

    # # Get upcoming events (not cancelled)
    # upcoming_events = Event.objects.filter(
    #     start_date__gte=timezone.now(),
    #     is_cancelled=False
    # ).order_by('start_date')[:5]  # Limit to 5 upcoming events

    # # Get recent events
    # recent_events = Event.objects.filter(
    #     start_date__lt=timezone.now()
    # ).order_by('-start_date')[:3]  # Limit to 3 recent events

    # # Count statistics
    # total_events = Event.objects.count()
    # cancelled_events = Event.objects.filter(is_cancelled=True).count()
    # active_events = total_events - cancelled_events

    # # Locations statistics
    # location_count = EventLocation.objects.count()

    return render(
        request,
        "event_dashboard/main.html",
        {
            "responsible_events": 1,
            "public_events": 2,
            "upcoming_events": 3,
            "recent_events": 4,
            "total_events": 5,
            "active_events": 6,
            "cancelled_events": 7,
            "location_count": 8,
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
        "event_permission_create/main.html",
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
    slug = event.slug

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
        "event_permission_update/main.html",
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
    
    return render(
        request,
        "event_permission_detail/main.html",
        {
            "permission": permission,
            "event": permission.event,
        },
    )


@login_required
def event_booking_type_create(request, slug):
    """
    View to create a new booking option for an event.
    """
    event = get_object_or_404(Event, slug=slug)

    if request.method == "POST":
        form = BookingOptionForm(request.POST)
        if form.is_valid():
            booking_option = form.save(commit=False)
            booking_option.event = event
            booking_option.created_by = request.user
            booking_option.save()
            return redirect("event-detail-booking-type", slug=slug)
    else:
        form = BookingOptionForm()
    
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
        form = BookingOptionForm(request.POST, instance=booking_option)
        if form.is_valid():
            updated_option = form.save(commit=False)
            updated_option.updated_by = request.user
            updated_option.save()
            return redirect("event-detail-booking-type", slug=slug)
    else:
        form = BookingOptionForm(instance=booking_option)
    
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
        "event_permission_detail/main.html",
        {
            "booking_option": booking_option,
            "event": event,
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
            "attributes": attributes,
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
        },
    )