from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import NutritionalTag
from .forms import NutritionalTagForm
from django.core.paginator import Paginator
from .forms import ScoutHierarchySearchForm, ZipCodeSearchForm, ZipCodeForm, UserSearchForm
from .models import ScoutHierarchy, ZipCode
from django.contrib import messages
import csv
from django.http import HttpResponse
from django.db.models import Q
from .forms import EventLocationForm, EventLocationSearchForm, NutritionalTagSearchForm, ScoutHierarchyForm, UserSearchForm
from .models import EventLocation

def main_view(request):

    context = {}

    return render(request, "master_data_main.html", context)


def masterdata_scout_hierarchy_dashboard(request):
    kpi_bund = ScoutHierarchy.objects.filter(level_choice="Bund").count()
    kpi_stamm = ScoutHierarchy.objects.filter(level_choice="Stamm").count()

    context = {
        "kpi_bund": kpi_bund,
        "kpi_stamm": kpi_stamm,
    }
    return render(request, "scout_hierarchy/dashboard/main.html", context)


def masterdata_scout_hierarchy_list(request):
    plans = ScoutHierarchy.objects.all()
    form = ScoutHierarchySearchForm(request.GET)

    if form.is_valid():
        query = form.cleaned_data.get("query")
        level = form.cleaned_data.get("level")
        status = form.cleaned_data.get("status")

        if query:
            plans = plans.filter(name__icontains=query)
        if level:
            plans = plans.filter(level_choice=level)
        if status:
            plans = plans.filter(status=status)

    paginator = Paginator(plans, per_page=20)
    page_num = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_num)
    page_obj.adjusted_elided_pages = paginator.get_elided_page_range(page_num)

    context = {
        "page_obj": page_obj,
        "form": form,
    }
    return render(request, "scout_hierarchy/list/main.html", context)

def masterdata_scout_hierarchy_overview(request, scout_hierarchy_id):
    scout_hierarchy = ScoutHierarchy.objects.get(id=scout_hierarchy_id)
    breadcrumbs = [
        {'name': 'Stammdaten', 'url': '/master-data/basic'},
        {'name': 'Gruppen', 'url': '/master-data/scout-hierarchy/dashboard'},
        {'name': scout_hierarchy.name, 'active': True},
        {'name': 'Übersicht', 'active': True}
    ]
    context = {
        "scout_hierarchy": scout_hierarchy,
        "breadcrumbs": breadcrumbs,
    }
    return render(request, "scout_hierarchy/detail/overview/main.html", context)


def masterdata_scout_hierarchy_manage(request, scout_hierarchy_id):
    scout_hierarchy = ScoutHierarchy.objects.get(id=scout_hierarchy_id)
    breadcrumbs = [
        {'name': 'Stammdaten', 'url': '/master-data/basic'},
        {'name': 'Gruppen', 'url': '/master-data/scout-hierarchy/dashboard'},
        {'name': scout_hierarchy.name, 'url': f'/master-data/scout-hierarchy/{scout_hierarchy_id}/overview'},
        {'name': 'Verwalten', 'active': True}
    ]
    context = {
        "scout_hierarchy": scout_hierarchy,
        "breadcrumbs": breadcrumbs,
    }
    return render(request, "scout_hierarchy/detail/manage/main.html", context)


def masterdata_scout_hierarchy_download(request, scout_hierarchy_id):
    scout_hierarchy = ScoutHierarchy.objects.get(id=scout_hierarchy_id)
    breadcrumbs = [
        {'name': 'Stammdaten', 'url': '/master-data/basic'},
        {'name': 'Gruppen', 'url': '/master-data/scout-hierarchy/dashboard'},
        {'name': scout_hierarchy.name, 'url': f'/master-data/scout-hierarchy/{scout_hierarchy_id}/overview'},
        {'name': 'Downloads', 'active': True}
    ]
    context = {
        "scout_hierarchy": scout_hierarchy,
        "breadcrumbs": breadcrumbs,
    }
    return render(request, "scout_hierarchy/detail/download/main.html", context)

def masterdata_scout_hierarchy_user(request, scout_hierarchy_id):
    scout_hierarchy = ScoutHierarchy.objects.get(id=scout_hierarchy_id)
    # Get all persons attached to this hierarchy
    persons = scout_hierarchy.persons.all()

    # Get users associated with these persons
    users = [person.user for person in persons if person.user]

    # Remove duplicates
    users = list(set(users))
    
    # Apply search filters
    form = UserSearchForm(request.GET)
    if form.is_valid():
        query = form.cleaned_data.get("query")
        if query:
            # Filter users by username, first_name, last_name or email
            filtered_users = []
            for user in users:
                if (query.lower() in user.username.lower() or 
                    query.lower() in user.first_name.lower() or 
                    query.lower() in user.last_name.lower() or 
                    query.lower() in user.email.lower()):
                    filtered_users.append(user)
            users = filtered_users

    # paginate users
    paginator = Paginator(users, per_page=20)
    page_num = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_num)
    page_obj.adjusted_elided_pages = paginator.get_elided_page_range(page_num)

    breadcrumbs = [
        {'name': 'Stammdaten', 'url': '/master-data/basic'},
        {'name': 'Gruppen', 'url': '/master-data/scout-hierarchy/dashboard'},
        {'name': scout_hierarchy.name, 'url': f'/master-data/scout-hierarchy/{scout_hierarchy_id}/overview'},
        {'name': 'Benutzer', 'active': True}
    ]

    context = {
        "scout_hierarchy": scout_hierarchy,
        "page_obj": page_obj,
        "breadcrumbs": breadcrumbs,
        "form": form,
    }
    return render(request, "scout_hierarchy/detail/user/main.html", context)


def scout_hierarchy_create(request):
    if request.method == "POST":
        form = ScoutHierarchyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("master-data-scout-hierarchy-list")
    else:
        form = ScoutHierarchyForm()

    context = {
        "form": form,
    }
    return render(request, "scout_hierarchy/create_update_form.html", context)


def scout_hierarchy_update(request, scout_hierarchy_id):
    scout_hierarchy = ScoutHierarchy.objects.get(id=scout_hierarchy_id)
    if request.method == "POST":
        form = ScoutHierarchyForm(request.POST, instance=scout_hierarchy)
        if form.is_valid():
            form.save()
            return redirect("master-data-scout-hierarchy-list")
    else:
        form = ScoutHierarchyForm(instance=scout_hierarchy)

    context = {
        "form": form,
        "scout_hierarchy": scout_hierarchy,
    }
    return render(request, "scout_hierarchy/create_update_form.html", context)


def scout_hierarchy_delete(request, scout_hierarchy_id):
    scout_hierarchy = get_object_or_404(ScoutHierarchy, id=scout_hierarchy_id)
    
    # Check if the object has children (to prevent orphaned records)
    if scout_hierarchy.children.exists():
        messages.error(request, "Diese Gruppe kann nicht gelöscht werden, da sie untergeordnete Gruppen enthält.")
        return redirect("master-data-scout-hierarchy-manage", scout_hierarchy_id=scout_hierarchy_id)
    
    if request.method == "POST":
        scout_hierarchy.delete()
        messages.success(request, f"{scout_hierarchy.name} wurde erfolgreich gelöscht.")
        return redirect("master-data-scout-hierarchy-list")
        
    context = {
        "scout_hierarchy": scout_hierarchy,
    }
    return render(request, "scout_hierarchy/delete_confirmation.html", context)


def scout_hierarchy_download_csv(request, scout_hierarchy_id):
    # Get the requested hierarchy object
    scout_hierarchy = get_object_or_404(ScoutHierarchy, id=scout_hierarchy_id)
    
    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{scout_hierarchy.name}_hierarchy.csv"'
    
    # Create CSV writer
    writer = csv.writer(response)
    
    # Write header row
    writer.writerow([
        "Name",'Slug', 'Abkürzung', 'Vollständiger Name', 'Beschreibung', 'Ebene', 
        'Postleitzahl', 'Stadt', 'Elternteil', 'Existiert seit', 'Existiert bis', 'Status'
    ])
    
    # Write data rows for the hierarchy and its children
    def write_hierarchy_to_csv(hierarchy, writer):
        writer.writerow([
            hierarchy.name,
            hierarchy.slug,
            hierarchy.abbreviation,
            hierarchy.full_name,
            hierarchy.description,
            hierarchy.level_choice,
            hierarchy.zip_code.zip_code if hierarchy.zip_code else "-",
            hierarchy.zip_code.city if hierarchy.zip_code else "-",
            hierarchy.parent.name if hierarchy.parent else "-",
            hierarchy.exist_from,
            hierarchy.exist_till,
            hierarchy.status
        ])
        
        # Recursively include all children
        for child in hierarchy.children.all():
            write_hierarchy_to_csv(child, writer)
    
    # Start the recursive writing with the requested hierarchy
    write_hierarchy_to_csv(scout_hierarchy, writer)
    
    return response



from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from .models import ZipCode
from django.db.models import Count

@require_GET
def zip_code_autocomplete(request):
    """View for handling autocomplete queries for zip codes"""
    params = request.GET

    query = list(params.values())[0] if params else ''

    if len(query) < 2:
        return HttpResponse('')
    
    # Search for matching zip codes
    zip_codes = ZipCode.objects.filter(zip_code__startswith=query)[:10]
    
    # Create a result list with zip code and city information
    results = [{'zip_code': z.zip_code, 'city': z.city} for z in zip_codes]
    
    print(f"Results: {results}")

    
    # Render a simple list of results
    return render(request, 'autocomplete/masterdata/zip_code_autocomplete_results.html', {
        'results': results,
    })

def masterdata_zip_code_dashboard(request):
    """Dashboard view for zip code management displaying key metrics."""
    # Count total zip codes
    total_zip_codes = ZipCode.objects.count()
    
    # Count zip codes by state using annotation
    states_distribution = ZipCode.objects.values('state').annotate(count=Count('id')).order_by('-count')
    
    # Get some statistical information
    cities_count = ZipCode.objects.values('city').distinct().count()
    
    context = {
        "total_zip_codes": total_zip_codes,
        "states_distribution": states_distribution,
        "cities_count": cities_count,
        "breadcrumbs": [
            {'name': 'Stammdaten', 'url': '/master-data/basic'},
            {'name': 'Postleitzahlen', 'active': True},
            {'name': 'Dashboard', 'active': True}
        ]
    }
    return render(request, "zip_code/dashboard/main.html", context)

# ZipCode Views
def masterdata_zip_code_list(request):
    zip_codes = ZipCode.objects.all().order_by('zip_code')
    form = ZipCodeSearchForm(request.GET)

    if form.is_valid():
        query = form.cleaned_data.get("query")
        state = form.cleaned_data.get("state")

        if query:
            zip_codes = zip_codes.filter(zip_code__icontains=query) | zip_codes.filter(city__icontains=query)
        if state:
            zip_codes = zip_codes.filter(state=state)

    paginator = Paginator(zip_codes, per_page=20)
    page_num = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_num)
    page_obj.adjusted_elided_pages = paginator.get_elided_page_range(page_num)

    context = {
        "page_obj": page_obj,
        "form": form,
    }
    return render(request, "zip_code/list/main.html", context)

def zip_code_create(request):
    if request.method == "POST":
        form = ZipCodeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Postleitzahl wurde erfolgreich erstellt.")
            return redirect("master-data-zip-code-list")
    else:
        form = ZipCodeForm()

    context = {
        "form": form,
    }
    return render(request, "zip_code/create_update_form.html", context)

def zip_code_update(request, zip_code_id):
    zip_code = get_object_or_404(ZipCode, id=zip_code_id)
    if request.method == "POST":
        form = ZipCodeForm(request.POST, instance=zip_code)
        if form.is_valid():
            form.save()
            messages.success(request, "Postleitzahl wurde erfolgreich aktualisiert.")
            return redirect("master-data-zip-code-list")
    else:
        form = ZipCodeForm(instance=zip_code)

    context = {
        "form": form,
        "zip_code": zip_code,
    }
    return render(request, "zip_code/create_update_form.html", context)

def zip_code_delete(request, zip_code_id):
    zip_code = get_object_or_404(ZipCode, id=zip_code_id)
    
    # Check if any ScoutHierarchy is using this zip code
    if ScoutHierarchy.objects.filter(zip_code=zip_code).exists():
        messages.error(request, "Diese Postleitzahl kann nicht gelöscht werden, da sie von Gruppen verwendet wird.")
        return redirect("master-data-zip-code-list")
    
    if request.method == "POST":
        zip_code.delete()
        messages.success(request, f"Postleitzahl {zip_code.zip_code} {zip_code.city} wurde erfolgreich gelöscht.")
        return redirect("master-data-zip-code-list")
        
    context = {
        "zip_code": zip_code,
    }
    return render(request, "zip_code/delete_confirmation.html", context)

def zip_code_download_csv(request):
    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="postleitzahlen.csv"'
    
    # Create CSV writer
    writer = csv.writer(response)
    
    # Write header row
    writer.writerow([
        "PLZ", 'Stadt', 'Bundesland', 'Breitengrad', 'Längengrad'
    ])
    
    # Write data rows
    for zip_code in ZipCode.objects.all().order_by('zip_code'):
        state_display = dict(StateChoices.choices).get(zip_code.state, zip_code.state)
        writer.writerow([
            zip_code.zip_code,
            zip_code.city,
            state_display,
            zip_code.lat,
            zip_code.lon
        ])
    
    return response


def masterdata_zip_code_overview(request, zip_code_id):
    """View for showing details about a specific zip code."""
    zip_code = get_object_or_404(ZipCode, id=zip_code_id)
    
    # Get all scout hierarchies that are using this zip code
    scout_hierarchies = ScoutHierarchy.objects.filter(zip_code=zip_code)
    
    # Paginate the scout hierarchies if there are many
    paginator = Paginator(scout_hierarchies, per_page=10)
    page_num = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_num)
    page_obj.adjusted_elided_pages = paginator.get_elided_page_range(page_num)
    
    breadcrumbs = [
        {'name': 'Stammdaten', 'url': '/master-data/basic'},
        {'name': 'Postleitzahlen', 'url': '/master-data/zip-code/dashboard'},
        {'name': f'{zip_code.zip_code} {zip_code.city}', 'active': True},
        {'name': 'Übersicht', 'active': True}
    ]
    
    context = {
        "zip_code": zip_code,
        "page_obj": page_obj,
        "breadcrumbs": breadcrumbs,
    }
    
    return render(request, "zip_code/detail/overview/main.html", context)


def masterdata_zip_code_manage(request, zip_code_id):
    """View for managing a specific zip code."""
    zip_code = get_object_or_404(ZipCode, id=zip_code_id)
    
    breadcrumbs = [
        {'name': 'Stammdaten', 'url': '/master-data/basic'},
        {'name': 'Postleitzahlen', 'url': '/master-data/zip-code/dashboard'},
        {'name': f'{zip_code.zip_code} {zip_code.city}', 'url': f'/master-data/zip-code/{zip_code_id}/overview'},
        {'name': 'Verwalten', 'active': True}
    ]
    
    context = {
        "zip_code": zip_code,
        "breadcrumbs": breadcrumbs,
    }
    
    return render(request, "zip_code/detail/manage/main.html", context)
    
# NutritionalTag Views
def nutritional_tag_list(request):
    nutritional_tags = NutritionalTag.objects.all().order_by('rank', 'name')
    form = NutritionalTagSearchForm(request.GET)
    
    if form.is_valid():
        query = form.cleaned_data.get("query")
        is_dangerous = form.cleaned_data.get("is_dangerous")
        
        if query:
            nutritional_tags = nutritional_tags.filter(
                Q(name__icontains=query) | 
                Q(description__icontains=query)
            )
        
        if is_dangerous:
            # Convert string 'True'/'False' to boolean
            is_dangerous_bool = is_dangerous == 'True'
            nutritional_tags = nutritional_tags.filter(is_dangerous=is_dangerous_bool)
    
    paginator = Paginator(nutritional_tags, per_page=20)
    page_num = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_num)
    page_obj.adjusted_elided_pages = paginator.get_elided_page_range(page_num)
    
    context = {
        "page_obj": page_obj,
        "form": form,
    }
    return render(request, 'nutritional_tag/list/main.html', context)

def nutritional_tag_detail_overview(request, pk):
    nutritional_tag = get_object_or_404(NutritionalTag, pk=pk)
    context = {
        "nutritional_tag": nutritional_tag,
        "breadcrumbs": [
            {'name': 'Stammdaten', 'url': '/master-data/basic'},
            {'name': 'Ernährungstags', 'url': '/master-data/nutritional-tags/list'},
            {'name': nutritional_tag.name, 'active': True},
            {'name': 'Übersicht', 'active': True}
        ]
    }
    return render(request, 'nutritional_tag/detail/overview/main.html', context)

# nutritional_tag_detail_manage
def nutritional_tag_detail_manage(request, pk):
    nutritional_tag = get_object_or_404(NutritionalTag, pk=pk)
    context = {
        "nutritional_tag": nutritional_tag,
        "breadcrumbs": [
            {'name': 'Stammdaten', 'url': '/master-data/basic'},
            {'name': 'Ernährungstags', 'url': '/master-data/nutritional-tags/list'},
            {'name': nutritional_tag.name, 'url': f'/master-data/nutritional-tags/{pk}/overview'},
            {'name': 'Verwalten', 'active': True}
        ]
    }
    return render(request, 'nutritional_tag/detail/manage/main.html', context)


def nutritional_tag_create(request):
    if request.method == "POST":
        form = NutritionalTagForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Nutritional tag was successfully created.")
            return redirect("nutritional-tag-list")
    else:
        form = NutritionalTagForm()

    context = {
        "form": form,
        "title": "Add Nutritional Tag",
        "button_text": "Create",
    }
    return render(request, 'nutritional_tag/form.html', context)

def nutritional_tag_update(request, pk):
    nutritional_tag = get_object_or_404(NutritionalTag, pk=pk)
    if request.method == "POST":
        form = NutritionalTagForm(request.POST, instance=nutritional_tag)
        if form.is_valid():
            form.save()
            messages.success(request, "Nutritional tag was successfully updated.")
            return redirect("nutritional-tag-list")
    else:
        form = NutritionalTagForm(instance=nutritional_tag)

    context = {
        "form": form,
        "nutritional_tag": nutritional_tag,
        "title": "Edit Nutritional Tag",
        "button_text": "Update",
    }
    return render(request, 'nutritional_tag/form.html', context)

def nutritional_tag_delete(request, pk):
    nutritional_tag = get_object_or_404(NutritionalTag, pk=pk)
    
    if request.method == "POST":
        nutritional_tag.delete()
        messages.success(request, f"Nutritional tag '{nutritional_tag.name}' was successfully deleted.")
        return redirect("nutritional-tag-list")
    
    context = {
        "nutritional_tag": nutritional_tag,
    }
    return render(request, 'nutritional_tag/confirm_delete.html', context)

def nutritional_tag_dashboard(request):
    """Dashboard view for nutritional tag management displaying key metrics."""
    # Count total tags
    total_tags = NutritionalTag.objects.count()
    
    # Get tags by category using annotation
    # category_distribution = NutritionalTag.objects.values('category').annotate(count=Count('id')).order_by('-count')
    
    # Get top tags by usage (if you have a relation to recipes or meals)
    # This is just a placeholder - adjust according to your actual model relationships
    # top_tags = NutritionalTag.objects.annotate(usage_count=Count('recipes')).order_by('-usage_count')[:5]
    
    breadcrumbs = [
        {'name': 'Stammdaten', 'url': '/master-data/basic'},
        {'name': 'Ernährungstags', 'active': True},
        {'name': 'Dashboard', 'active': True}
    ]
    
    context = {
        "total_tags": total_tags,
        "category_distribution": [13],
        # "top_tags": top_tags,
        "breadcrumbs": breadcrumbs
    }
    
    return render(request, "nutritional_tag/dashboard/main.html", context)

# EventLocation Views
def masterdata_event_location_dashboard(request):
    """Dashboard view for event location management displaying key metrics."""
    # Count total event locations
    total_event_locations = EventLocation.objects.count()
    
    # Count locations by state
    states_distribution = EventLocation.objects.filter(
        zip_code__isnull=False
    ).values(
        'zip_code__state'
    ).annotate(
        count=Count('id')
    ).order_by('-count')
    
    context = {
        "total_event_locations": 1,
        "states_distribution": states_distribution,
        "kpi_locations": total_event_locations,
        "breadcrumbs": [
            {'name': 'Stammdaten', 'url': '/master-data/basic'},
            {'name': 'Veranstaltungsorte', 'active': True},
            {'name': 'Dashboard', 'active': True}
        ]
    }
    return render(request, "master_event_location/dashboard/main.html", context)

def masterdata_event_location_list(request):
    """List view for event locations with search and filter functionality."""
    event_locations = EventLocation.objects.all().order_by('name')
    form = EventLocationSearchForm(request.GET)

    if form.is_valid():
        query = form.cleaned_data.get("query")
        state = form.cleaned_data.get("state")

        if query:
            event_locations = event_locations.filter(
                Q(name__icontains=query) |
                Q(zip_code__zip_code__icontains=query) |
                Q(zip_code__city__icontains=query) |
                Q(address__icontains=query)
            )
        if state:
            event_locations = event_locations.filter(zip_code__state=state)

    paginator = Paginator(event_locations, per_page=20)
    page_num = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_num)
    page_obj.adjusted_elided_pages = paginator.get_elided_page_range(page_num)

    context = {
        "page_obj": page_obj,
        "form": form,
        "breadcrumbs": [
            {'name': 'Stammdaten', 'url': '/master-data/basic'},
            {'name': 'Veranstaltungsorte', 'active': True},
            {'name': 'Liste', 'active': True}
        ]
    }
    return render(request, "master_event_location/list/main.html", context)

def masterdata_event_location_overview(request, event_location_id):
    """View for showing details about a specific event location."""
    event_location = get_object_or_404(EventLocation, id=event_location_id)
    
    breadcrumbs = [
        {'name': 'Stammdaten', 'url': '/master-data/basic'},
        {'name': 'Veranstaltungsorte', 'url': '/master-data/event-location/dashboard'},
        {'name': event_location.name, 'active': True},
        {'name': 'Übersicht', 'active': True}
    ]
    
    context = {
        "event_location": event_location,
        "breadcrumbs": breadcrumbs,
    }
    
    return render(request, "master_event_location/detail/overview/main.html", context)

def masterdata_event_location_manage(request, event_location_id):
    """View for managing a specific event location."""
    event_location = get_object_or_404(EventLocation, id=event_location_id)
    
    breadcrumbs = [
        {'name': 'Stammdaten', 'url': '/master-data/basic'},
        {'name': 'Veranstaltungsorte', 'url': '/master-data/event-location/dashboard'},
        {'name': event_location.name, 'url': f'/master-data/event-location/{event_location_id}/overview'},
        {'name': 'Verwalten', 'active': True}
    ]
    
    context = {
        "event_location": event_location,
        "breadcrumbs": breadcrumbs,
    }
    
    return render(request, "master_event_location/detail/manage/main.html", context)

def event_location_create(request):
    """View for creating a new event location."""
    if request.method == "POST":
        form = EventLocationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Veranstaltungsort wurde erfolgreich erstellt.")
            return redirect("master-data-event-location-list")
    else:
        form = EventLocationForm()

    context = {
        "form": form,
        "breadcrumbs": [
            {'name': 'Stammdaten', 'url': '/master-data/basic'},
            {'name': 'Veranstaltungsorte', 'url': '/master-data/event-location/dashboard'},
            {'name': 'Erstellen', 'active': True}
        ]
    }
    return render(request, "master_event_location/create_update_form.html", context)

def event_location_update(request, event_location_id):
    """View for updating an existing event location."""
    event_location = get_object_or_404(EventLocation, id=event_location_id)
    if request.method == "POST":
        form = EventLocationForm(request.POST, instance=event_location)
        if form.is_valid():
            form.save()
            messages.success(request, "Veranstaltungsort wurde erfolgreich aktualisiert.")
            return redirect("master-data-event-location-list")
    else:
        form = EventLocationForm(instance=event_location)

    context = {
        "form": form,
        "event_location": event_location,
        "breadcrumbs": [
            {'name': 'Stammdaten', 'url': '/master-data/basic'},
            {'name': 'Veranstaltungsorte', 'url': '/master-data/event-location/dashboard'},
            {'name': event_location.name, 'url': f'/master-data/event-location/{event_location_id}/overview'},
            {'name': 'Bearbeiten', 'active': True}
        ]
    }
    return render(request, "master_event_location/create_update_form.html", context)

def event_location_delete(request, event_location_id):
    """View for deleting an event location."""
    event_location = get_object_or_404(EventLocation, id=event_location_id)
    
    # Check if any related objects are using this event location
    # This would depend on your data model, for example:
    # if Event.objects.filter(location=event_location).exists():
    #    messages.error(request, "Dieser Veranstaltungsort kann nicht gelöscht werden, da er von Veranstaltungen verwendet wird.")
    #    return redirect("master-data-event-location-manage", event_location_id=event_location_id)
    
    if request.method == "POST":
        event_location.delete()
        messages.success(request, f"Veranstaltungsort '{event_location.name}' wurde erfolgreich gelöscht.")
        return redirect("master-data-event-location-list")
        
    context = {
        "event_location": event_location,
        "breadcrumbs": [
            {'name': 'Stammdaten', 'url': '/master-data/basic'},
            {'name': 'Veranstaltungsorte', 'url': '/master-data/event-location/dashboard'},
            {'name': event_location.name, 'url': f'/master-data/event-location/{event_location_id}/overview'},
            {'name': 'Löschen', 'active': True}
        ]
    }
    return render(request, "master_event_location/delete_confirmation.html", context)