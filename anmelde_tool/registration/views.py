from anmelde_tool.event.basic.models import (
    Event,
    EventLocation,
    EventPermission,
    BookingOption,
    EventModule,
)
from general.login.forms import PersonForm
from .models import Registration
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.utils.text import slugify
from formtools.wizard.views import SessionWizardView
from django.contrib import messages
from django.utils.decorators import method_decorator
from .forms import (
    RegistrationListFilter,
    RegistrationBaseForm,
)
from anmelde_tool.attributes.models import (
    AttributeModule,
    BooleanAttribute,
    StringAttribute,
    DateTimeAttribute,
    IntegerAttribute,
    FloatAttribute,
    TravelAttribute,
)
from django import forms
from django.forms import Form
from django.contrib.auth.mixins import LoginRequiredMixin
# from anmelde_tool.event.models import RegistrationData
from anmelde_tool.registration.forms import create_module_form_class


@login_required
def register_detail_overview(request, reg_id):
    """
    View for managing registration details.
    """
    register = get_object_or_404(Registration, id=reg_id)
    event = register.event

    return render(
        request,
        "registration_detail/overview/main.html",
        {
            "event": event,
            "reg": register,
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
                    travel_attr = TravelAttribute.objects.get(
                        attribute_module=attr_module, registration=register
                    )
                    attribute_data["value"] = {
                        "number_persons": travel_attr.number_persons,
                        "type_field": travel_attr.type_field,
                        "date_time_field": travel_attr.date_time_field,
                        "description": travel_attr.description,
                    }
                    attribute_data["id"] = travel_attr.id
                except TravelAttribute.DoesNotExist:
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
        },
    )


@login_required
def register_detail_permission(request, reg_id):
    """
    View for managing registration permissions.
    """
    register = get_object_or_404(Registration, id=reg_id)
    event = register.event
    permissions = EventPermission.objects.filter(event=event)

    # Set up pagination
    paginator = Paginator(permissions, 10)  # Show 10 participants per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "registration_detail/permission/main.html",
        {
            "event": event,
            "reg": register,
            "page_obj": page_obj,
        },
    )


@login_required
def register_detail_participant(request, reg_id):
    """
    View for managing registration participants.
    """
    register = get_object_or_404(Registration, id=reg_id)
    event = register.event
    
    # Get participants for this registration
    participants = register.registrationparticipant_set.all()
    
    # Set up pagination
    paginator = Paginator(participants, 10)  # Show 10 participants per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "registration_detail/participant/main.html",
        {
            "event": event,
            "reg": register,
            "page_obj": page_obj,
        },
    )


@login_required
def register_detail_privacy(request, reg_id):
    """
    View for managing registration privacy settings.
    """
    register = get_object_or_404(Registration, id=reg_id)
    event = register.event
    
    # You may want to add specific privacy-related queries here
    # For example, getting consent records, data processing agreements, etc.
    
    return render(
        request,
        "registration_detail/privacy/main.html",
        {
            "event": event,
            "reg": register,
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
            event__name__icontains=search_filter_form.cleaned_data.get("search", "")
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

@method_decorator(login_required, name='dispatch')
class RegistrationWizardView(SessionWizardView):
    template_name = "registration_create_wizard/generic_step.html"
    
    def get_form_initial(self, step):
        initial = self.initial_dict.get(step, {})
        # You can pre-populate form fields here if needed
        return initial
    
    def get_form_kwargs(self, step=None):
        kwargs = super().get_form_kwargs(step)
        if step:
            event_slug = self.kwargs.get('event_slug')
            event = get_object_or_404(Event, slug=event_slug)
            # Get event module for this step
            event_modules = list(EventModule.objects.filter(event=event).order_by('ordering'))
            step_index = int(step)
            if step_index < len(event_modules):
                kwargs['event_module'] = event_modules[step_index]
        return kwargs
    
    def get_form_list(self):
        """
        Dynamically create forms for each event module
        """
        event_slug = self.kwargs.get('event_slug')
        event = get_object_or_404(Event, slug=event_slug)
        event_modules = EventModule.objects.filter(event=event)
        
        form_list = {}
        for i, event_module in enumerate(event_modules):

            if event_module.name == "Participants":
                form_list[str(i)] = PersonForm
            else:
                # Create a form class for this event module
                form_class = create_module_form_class(event_module)
                form_list[str(i)] = form_class

            
        return form_list
    
    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        event_slug = self.kwargs.get('event_slug')
        event = get_object_or_404(Event, slug=event_slug)
        event_modules = list(EventModule.objects.filter(event=event).order_by('ordering'))
        context['event'] = event
        context['event_modules'] = event_modules
        context['event_module'] = event_modules[int(self.steps.current)]

        return context
        
    def done(self, form_list, **kwargs):
        """
        Process the form data when all steps are complete
        """
        event_slug = self.kwargs.get('event_slug')
        event = get_object_or_404(Event, slug=event_slug)
        event_modules = list(EventModule.objects.filter(event=event))
        
        # Create a registration
        registration = Registration.objects.create(
            event=event,
        )
        
        # Save all form data
        for i, form in enumerate(form_list):
            if i < len(event_modules):
                event_module = event_modules[i]
                form_data = form.cleaned_data
                
                for field_name, value in form_data.items():
                    # Extract attribute module ID from field name (e.g., 'attribute_123')
                    if field_name.startswith('attribute_'):
                        attribute_id = int(field_name.split('_')[1])
                        attribute_module = AttributeModule.objects.get(id=attribute_id)
                        
                        # Create or update the attribute based on its type
                        if attribute_module.field_type == 'BoA':
                            # Default to False if value is None
                            boolean_value = False if value is None else bool(value)
                            BooleanAttribute.objects.create(
                                registration=registration,
                                attribute_module=attribute_module,
                                boolean_field=boolean_value
                            )
                        elif attribute_module.field_type == 'StA':
                            # Convert to empty string if None
                            string_value = '' if value is None else str(value)
                            StringAttribute.objects.create(
                                registration=registration,
                                attribute_module=attribute_module,
                                string_field=string_value
                            )
                        elif attribute_module.field_type == 'InA':
                            # Default to 0 if None or not convertible to int
                            try:
                                integer_value = 0 if value is None else int(value)
                            except (ValueError, TypeError):
                                integer_value = 0
                            IntegerAttribute.objects.create(
                                registration=registration,
                                attribute_module=attribute_module,
                                integer_field=integer_value
                            )
                        elif attribute_module.field_type == 'FlA':
                            # Default to 0.0 if None or not convertible to float
                            try:
                                float_value = 0.0 if value is None else float(value)
                            except (ValueError, TypeError):
                                float_value = 0.0
                            FloatAttribute.objects.create(
                                registration=registration,
                                attribute_module=attribute_module,
                                float_field=float_value
                            )
                        elif attribute_module.field_type == 'TiA':
                            # Don't provide date_time_field if value is None
                            kwargs = {
                                'registration': registration,
                                'attribute_module': attribute_module
                            }
                            if value is not None:
                                kwargs['date_time_field'] = value
                            DateTimeAttribute.objects.create(**kwargs)
                        elif attribute_module.field_type == 'TrA':
                            # For travel attributes, we expect value to be either a dictionary
                            # or we need to parse it from form data with specific field names
                            if isinstance(value, dict):
                                travel_data = value
                            else:
                                # If it's not a dictionary, use default values
                                travel_data = {
                                    'number_persons': 1,
                                    'type_field': 'Train',
                                    'date_time_field': None,
                                    'description': value if value else ''
                                }
                                
                                # Try to get related fields from the form data
                                persons_field = f'attribute_{attribute_id}_persons'
                                type_field = f'attribute_{attribute_id}_type'
                                datetime_field = f'attribute_{attribute_id}_datetime'
                                desc_field = f'attribute_{attribute_id}_description'
                                
                                if persons_field in form_data:
                                    travel_data['number_persons'] = form_data[persons_field]
                                if type_field in form_data:
                                    travel_data['type_field'] = form_data[type_field]
                                if datetime_field in form_data:
                                    travel_data['date_time_field'] = form_data[datetime_field]
                                if desc_field in form_data:
                                    travel_data['description'] = form_data[desc_field]
                            
                            TravelAttribute.objects.create(
                                registration=registration,
                                attribute_module=attribute_module,
                                number_persons=int(travel_data.get('number_persons', 1)),
                                type_field=travel_data.get('type_field', 'Train'),
                                date_time_field=travel_data.get('date_time_field'),
                                description=travel_data.get('description', '')
                            )
        # Redirect to the registration overview page
        messages.success(self.request, 'Registration completed successfully!')
        return redirect(reverse('reg-detail-overview', kwargs={'reg_id': registration.id}))