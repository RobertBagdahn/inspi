from anmelde_tool.attributes.choices import TravelType, AttributeType
from anmelde_tool.attributes.models import (
    AttributeModule,
    BooleanAttribute,
    IntegerAttribute,
    FloatAttribute,
    StringAttribute,
    DateTimeAttribute,
    TravelAttribute,
)
from anmelde_tool.attributes.forms import (
    BooleanAttributeForm,
    DateTimeAttributeForm,
    IntegerAttributeForm,
    FloatAttributeForm,
    StringAttributeForm,
    TravelAttributeForm,
    GeneralAttributeForm,
)

from anmelde_tool.registration.models import Registration
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.urls import reverse


@login_required
def attributes_edit(request, attribute_id):
    """
    View to edit attributes of a registration.
    """

    # Map attribute models to their forms
    attribute_types = {
        BooleanAttribute: BooleanAttributeForm,
        IntegerAttribute: IntegerAttributeForm,
        FloatAttribute: FloatAttributeForm,
        StringAttribute: StringAttributeForm,
        DateTimeAttribute: DateTimeAttributeForm,
        TravelAttribute: TravelAttributeForm,
    }

    # Try to find the attribute in each model type
    attribute = None
    form_class = None

    for model, form in attribute_types.items():
        try:
            attribute = model.objects.get(id=attribute_id)
            form_class = form
            break
        except model.DoesNotExist:
            continue

    if attribute is None:
        # If no attribute found with this ID
        return redirect(
            "reg-detail-overview"
        )  # Redirect to a safe page if no attribute found

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
        {"form": form, "attribute_module": attribute_module},
    )


@login_required
def attributes_delete(request, attribute_id):
    """
    View to delete attributes of a registration.
    """

    attribute = get_object_or_404(BooleanAttribute, id=attribute_id)

    # Get the registration ID and attribute module
    attribute_module = attribute.attribute_module
    reg_id = attribute_module.registration.id

    if request.method == "POST":
        # Delete the attribute instance and redirect to the registration detail page
        attribute.delete()
        return redirect("reg-detail-overview", reg_id)

    return render(
        request,
        "attributes_edit/delete.html",
        {"attribute": attribute, "attribute_module": attribute_module},
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

    # Handle form submission
    if request.method == "POST":
        # Determine which form to use based on the attribute type
        attribute_type = attribute_module.field_type
        if attribute_type == "BoA":
            form = BooleanAttributeForm(request.POST)
        elif attribute_type == "InA":
            form = IntegerAttributeForm(request.POST)
        elif attribute_type == "FlA":
            form = FloatAttributeForm(request.POST)
        elif attribute_type == "StA":
            form = StringAttributeForm(request.POST)
        elif attribute_type == "TiA":
            form = DateTimeAttributeForm(request.POST)
        elif attribute_type == "TrA":
            form = TravelAttributeForm(request.POST)
        else:
            # Default to string attribute if type is not specified
            form = StringAttributeForm(request.POST)
        if form.is_valid():
            # Create a new attribute instance and save it
            attribute = form.save(commit=False)
            attribute.attribute_module = attribute_module
            attribute.registration = registration
            attribute.save()
            return redirect("reg-detail-overview", registration.id)
    else:
        # Determine which form to use based on the attribute type
        attribute_type = attribute_module.field_type
        if attribute_type == "BoA":
            form = BooleanAttributeForm()
        elif attribute_type == "InA":
            form = IntegerAttributeForm()
        elif attribute_type == "FlA":
            form = FloatAttributeForm()
        elif attribute_type == "StA":
            form = StringAttributeForm()
        elif attribute_type == "TiA":
            form = DateTimeAttributeForm()
        elif attribute_type == "TrA":
            form = TravelAttributeForm()
        else:
            # Default to string attribute if type is not specified
            form = StringAttributeForm()

    return render(
        request,
        "attributes_create/main.html",
        {
            "form": form,
            "registration": registration,
            "attribute_module": attribute_module,
        },
    )


@login_required
def attribute_detail(request, attribute_id):
    """
    View to display details of a specific attribute.
    """

    attribute = AttributeModule.objects.get(id=attribute_id)

    return render(
        request,
        "attributes_detail/main.html",
        {
            "attribute": attribute,
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
            return redirect("attribute-detail", attribute_id=attribute.id)
    else:
        form = GeneralAttributeForm(instance=attribute)
    
    return render(
        request,
        "attributes_update/main.html",
        {
            "form": form,
            "attribute": attribute,
        },
    )


@login_required
def attribute_delete(request, attribute_id):
    """
    View to delete an attribute module.
    """
    attribute = get_object_or_404(AttributeModule, id=attribute_id)
    
    if request.method == "POST":
        # Store the return URL before deleting
        return_url = reverse("reg-detail-overview", args=[attribute.registration.id]) if attribute.registration else reverse("home")
        
        # Delete the attribute
        attribute.delete()
        
        return redirect(return_url)
    
    return render(
        request,
        "attributes_delete/main.html",
        {
            "attribute": attribute,
        },
    )