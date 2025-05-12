from anmelde_tool.attributes.choices import TravelType, AttributeType
from anmelde_tool.attributes.models import (
    AttributeModule,
    BooleanAttribute,
    IntegerAttribute,
    FloatAttribute,
    StringAttribute,
    DateTimeAttribute,
    HTMLAttribute,
    RadioAttribute,
    MultiSelectAttribute,
    ZipCodeAttribute,
    EmailAttribute,
    PhoneAttribute,
    DateAttribute,
    ScoutGroupAttribute,
    AttributeChoiceOption,
)
from anmelde_tool.attributes.forms import (
    BooleanAttributeForm,
    DateTimeAttributeForm,
    IntegerAttributeForm,
    FloatAttributeForm,
    StringAttributeForm,
    GeneralAttributeForm,
    DateAttributeForm,
    HTMLAttributeForm,
    RadioAttributeForm,
    MultiSelectAttributeForm,
    ZipCodeAttributeForm,
    EmailAttributeForm,
    PhoneAttributeForm,
    ScoutGroupAttributeForm,
    AttributeChoiceOptionForm,
)


from anmelde_tool.registration.models import Registration
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.urls import reverse


def get_attribute_module_by_id(attribute_id):
    """
    Helper function to get an attribute module by its ID.
    """
    attribute_types = {
        BooleanAttribute: BooleanAttributeForm,
        IntegerAttribute: IntegerAttributeForm,
        FloatAttribute: FloatAttributeForm,
        StringAttribute: StringAttributeForm,
        DateTimeAttribute: DateTimeAttributeForm,
        DateAttribute: DateAttributeForm,
        HTMLAttribute: HTMLAttributeForm,
        RadioAttribute: RadioAttributeForm,
        MultiSelectAttribute: MultiSelectAttributeForm,
        ZipCodeAttribute: ZipCodeAttributeForm,
        EmailAttribute: EmailAttributeForm,
        PhoneAttribute: PhoneAttributeForm,
        ScoutGroupAttribute: ScoutGroupAttributeForm,
    }

    # Try to find the attribute in each model type
    attribute = None
    form_class = None

    print(attribute_id)

    for model, form in attribute_types.items():
        print(model)
        try:
            attribute = model.objects.get(id=attribute_id)
            form_class = form
            # If we found the attribute, break out of the loop
            print(attribute)
            print(form_class)
            if attribute:
                print(attribute)
                print(form_class)

            break
        except model.DoesNotExist:
            print(f"{model.__name__} with ID {attribute_id} does not exist.")
            continue

    if attribute is None:
        # If no attribute found with this ID
        return None, None
    return attribute, form_class


@login_required
def attributes_edit(request, attribute_id):
    """
    View to edit attributes of a registration.
    """

    attribute, form_class = get_attribute_module_by_id(attribute_id)

    # Get the registration ID and attribute module
    attribute_module = attribute.attribute_module
    reg_id = attribute.registration.id

    if request.method == "POST":
        form = form_class(request.POST, instance=attribute)
        if form.is_valid():
            form.save()
            return redirect("reg-detail-overview", reg_id)
    else:
        form = form_class(instance=attribute)

    return render(
        request,
        "attributes_edit/main.html",
        {
            "form": form,
            "attribute_module": attribute_module,
            "breadcrumbs": [
                {
                    "url": reverse("reg-detail-overview", args=[reg_id]),
                    "name": _("Registration"),
                },
                {
                    "url": reverse(
                        "event-attribute-detail", args=[attribute_module.id]
                    ),
                    "name": _("Attribute Module"),
                },
                {
                    "url": reverse("attributes-edit", args=[attribute.id]),
                    "name": _("Edit Attribute"),
                },
            ],
        },
    )


@login_required
def attributes_delete(request, attribute_id):
    """
    View to delete attributes of a registration.
    """

    attribute = get_object_or_404(AttributeModule, id=attribute_id)

    if attribute is None:
        # Handle case where attribute doesn't exist
        return redirect("event-list")

    if request.method == "POST":
        attribute.delete()

        # Get the event module ID before deleting the attribute
        event_module_id = attribute.event_module.id
        return redirect("event-module-detail", event_module_id)

    return render(
        request,
        "attributes_delete/main.html",
        {
            "attribute": attribute,
        },
    )


@login_required
def attributes_create(request, registration_id, attribute_module_id):
    """
    View to create attributes of a registration.
    """

    # Get the registration instance
    registration = get_object_or_404(Registration, id=registration_id)

    # Get the attribute module instance
    attribute_module = get_object_or_404(AttributeModule, id=attribute_module_id)

    # Define attribute_forms dictionary
    attribute_forms = {
        "BoA": BooleanAttributeForm,
        "InA": IntegerAttributeForm,
        "FlA": FloatAttributeForm,
        "StA": StringAttributeForm,
        "TiA": DateTimeAttributeForm,
        "DaA": DateAttributeForm,
        "HtA": HTMLAttributeForm,
        "RaA": RadioAttributeForm,
        "MuA": MultiSelectAttributeForm,
        "ZiA": ZipCodeAttributeForm,
        "EmA": EmailAttributeForm,
        "PhA": PhoneAttributeForm,
        "ScA": ScoutGroupAttributeForm,
    }

    # Handle form submission
    if request.method == "POST":
        # Determine which form to use based on the attribute type
        attribute_type = attribute_module.field_type
        form_class = attribute_forms.get(attribute_type, StringAttributeForm)
        form = form_class(request.POST)

        if form.is_valid():
            # Create a new attribute instance and save it
            attribute = form.save(commit=False)
            attribute.attribute_module = attribute_module
            attribute.registration = registration
            attribute.save()

            # Handle many-to-many relationships (for MultiSelectAttribute)
            if hasattr(form, "save_m2m"):
                form.save_m2m()

            return redirect("reg-detail-overview", registration.id)
    else:
        # Determine which form to use based on the attribute type
        attribute_type = attribute_module.field_type
        form_class = attribute_forms.get(attribute_type, StringAttributeForm)
        form = form_class()

    return render(
        request,
        "attributes_create/main.html",
        {
            "form": form,
            "registration": registration,
            "attribute_module": attribute_module,
            "breadcrumbs": [
                {
                    "url": reverse("reg-detail-overview", args=[registration.id]),
                    "name": _("Registration"),
                },
                {
                    "url": reverse(
                        "event-attribute-detail", args=[attribute_module.id]
                    ),
                    "name": _("Attribute Module"),
                },
                {
                    "url": reverse(
                        "attributes-create", args=[registration.id, attribute_module.id]
                    ),
                    "name": _("Create Attribute"),
                },
            ],
        },
    )


@login_required
def attribute_detail(request, attribute_id):
    """
    View to display details of a specific attribute.
    """

    attribute = AttributeModule.objects.get(id=attribute_id)

    # Get all the attributes of the AttributeModule instance
    attribute_properties = {
        "id": attribute.id,
        "title": attribute.title,
        "field_type": attribute.field_type,
    }

    # Get related choices if this attribute has choices (like Radio or MultiSelect)
    choices = AttributeChoiceOption.objects.filter(attribute_module=attribute)

    return render(
        request,
        "attributes_detail/main.html",
        {
            "attribute": attribute,
            "choices": choices,
            "update_url": reverse("attributes-update", args=[attribute_id]),
            "breadcrumbs": [
                {
                    "url": reverse("event-list"),
                    "name": _("Veranstaltungen"),
                },
                {
                    "url": reverse(
                        "event-detail-module", args=[attribute.event_module.event.slug]
                    ),
                    "name": attribute.event_module.event.name,
                },
                {
                    "url": reverse(
                        "event-detail-module", args=[attribute.event_module.id]
                    ),
                    "name": _("Attribute"),
                },
                {
                    "url": reverse(
                        "event-module-detail", args=[attribute.event_module.id]
                    ),
                    "name": attribute.event_module.header,
                },
                {
                    "url": reverse("event-attribute-detail", args=[attribute.id]),
                    "name": attribute.title,
                },
            ],
        },
    )


@login_required
def attribute_update(request, attribute_id):
    """
    View to update an attribute module.
    """
    attribute = get_object_or_404(AttributeModule, id=attribute_id)

    if request.method == "POST":
        form = GeneralAttributeForm(request.POST, instance=attribute)
        if form.is_valid():
            form.save()
            return redirect("event-attribute-detail", attribute_id=attribute.id)
    else:
        form = GeneralAttributeForm(instance=attribute)

    return render(
        request,
        "attributes_update/main.html",
        {
            "form": form,
            "attribute": attribute,
            "breadcrumbs": [
                {
                    "url": reverse("event-attribute-detail", args=[attribute.id]),
                    "name": _("Attribute"),
                },
                {
                    "url": reverse("attributes-update", args=[attribute.id]),
                    "name": _("Update Attribute"),
                },
            ],
        },
    )


@login_required
def attribute_delete(request, attribute_id):
    """
    View to delete an attribute module.
    """
    attribute = get_object_or_404(AttributeModule, id=attribute_id)

    if request.method == "POST":
        return_url = (
            reverse("reg-detail-overview", args=[attribute.registration.id])
            if attribute.registration
            else reverse("home")
        )
        # Delete the attribute
        attribute.delete()
        return redirect(return_url)
    return render(
        request,
        "attributes_delete/main.html",
        {
            "attribute": attribute,
            "breadcrumbs": [
                {
                    "url": reverse("event-attribute-detail", args=[attribute.id]),
                    "name": _("Attribute"),
                },
                {
                    "url": reverse("attributes-delete", args=[attribute.id]),
                    "name": _("Delete Attribute"),
                },
            ],
        },
    )


@login_required
def attribute_choice_create(request, attribute_id):
    """
    View to create a new choice option for an attribute.
    """
    attribute = get_object_or_404(AttributeModule, id=attribute_id)

    if request.method == "POST":
        form = AttributeChoiceOptionForm(request.POST)
        if form.is_valid():
            choice = form.save(commit=False)
            choice.attribute_module = attribute
            choice.save()
            return redirect("event-attribute-detail", attribute_id=attribute.id)
    else:
        form = AttributeChoiceOptionForm()

    return render(
        request,
        "attributes_detail/choice-create.html",
        {
            "form": form,
            "attribute": attribute,
            "breadcrumbs": [
                {"url": reverse("event-list"), "name": _("Veranstaltungen")},
                {
                    "url": reverse(
                        "event-detail-module", args=[attribute.event_module.event.slug]
                    ),
                    "name": attribute.event_module.event.name,
                },
                {
                    "url": reverse("event-attribute-detail", args=[attribute.id]),
                    "name": attribute.title,
                },
                {
                    "url": reverse("attribute-choice-create", args=[attribute.id]),
                    "name": _("Option hinzufügen"),
                },
            ],
        },
    )


@login_required
def attribute_choice_edit(request, choice_id):
    """
    View to edit a choice option.
    """
    choice = get_object_or_404(AttributeChoiceOption, id=choice_id)
    attribute = choice.attribute_module

    if request.method == "POST":
        form = AttributeChoiceOptionForm(request.POST, instance=choice)
        if form.is_valid():
            form.save()
            return redirect("event-attribute-detail", attribute_id=attribute.id)
    else:
        form = AttributeChoiceOptionForm(instance=choice)

    return render(
        request,
        "attributes_detail/choice-edit.html",
        {
            "form": form,
            "choice": choice,
            "attribute": attribute,
            "breadcrumbs": [
                {"url": reverse("event-list"), "name": _("Veranstaltungen")},
                {
                    "url": reverse(
                        "event-detail-module", args=[attribute.event_module.event.slug]
                    ),
                    "name": attribute.event_module.event.name,
                },
                {
                    "url": reverse("event-attribute-detail", args=[attribute.id]),
                    "name": attribute.title,
                },
                {
                    "url": reverse("attribute-choice-edit", args=[choice.id]),
                    "name": _("Option bearbeiten"),
                },
            ],
        },
    )


@login_required
def attribute_choice_delete(request, choice_id):
    """
    View to delete a choice option.
    """
    choice = get_object_or_404(AttributeChoiceOption, id=choice_id)
    attribute = choice.attribute_module

    if request.method == "POST":
        choice.delete()
        return redirect("event-attribute-detail", attribute_id=attribute.id)

    return render(
        request,
        "attributes_detail/choice-delete.html",
        {
            "choice": choice,
            "attribute": attribute,
            "breadcrumbs": [
                {"url": reverse("event-list"), "name": _("Veranstaltungen")},
                {
                    "url": reverse(
                        "event-detail-module", args=[attribute.event_module.event.slug]
                    ),
                    "name": attribute.event_module.event.name,
                },
                {
                    "url": reverse("event-attribute-detail", args=[attribute.id]),
                    "name": attribute.title,
                },
                {
                    "url": reverse("attribute-choice-delete", args=[choice.id]),
                    "name": _("Option löschen"),
                },
            ],
        },
    )
