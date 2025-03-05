from django.shortcuts import render
from django.core.paginator import Paginator
from .forms import ScoutHierarchySearchForm
from .models import ScoutHierarchy
from django.shortcuts import redirect, get_object_or_404
from .forms import ScoutHierarchyForm
from django.contrib import messages
import csv
from django.http import HttpResponse


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
    context = {
        "scout_hierarchy": scout_hierarchy,
    }
    return render(request, "scout_hierarchy/detail/overview/main.html", context)


def masterdata_scout_hierarchy_manage(request, scout_hierarchy_id):
    scout_hierarchy = ScoutHierarchy.objects.get(id=scout_hierarchy_id)
    context = {
        "scout_hierarchy": scout_hierarchy,
    }
    return render(request, "scout_hierarchy/detail/manage/main.html", context)


def masterdata_scout_hierarchy_download(request, scout_hierarchy_id):
    scout_hierarchy = ScoutHierarchy.objects.get(id=scout_hierarchy_id)
    context = {
        "scout_hierarchy": scout_hierarchy,
    }
    return render(request, "scout_hierarchy/detail/download/main.html", context)


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