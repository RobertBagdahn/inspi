import os
from django.http import FileResponse
from activity.activity.models import Activity
from django.shortcuts import redirect, render
from .forms import ImageDownloadForm
from django.template.loader import get_template

import io


def generate_png_from_svg(request, activity_id, color, page):
    activity = Activity.objects.get(id=activity_id)

    template_path = f"svg/heimabend_der_woche_{page}.svg"

    words = activity.summary.split("<br />")
    words = [
        item
        for sublist in [word.split() for word in activity.summary.split("<br />")]
        for item in sublist
    ]

    words_20_chars = []
    current_word = ""

    for word in words:
        if word == "<br />":
            if current_word:
                words_20_chars.append(current_word)
                current_word = ""
            words_20_chars.append("")
        elif len(current_word) + len(word) + 1 > 32:
            words_20_chars.append(current_word)
            current_word = word
        else:
            if current_word:
                current_word += " " + word
            else:
                current_word = word

    if current_word:
        words_20_chars.append(current_word)

    title_ary = activity.title.split(" ")

    current_title = []
    temp_str = ""

    for word in title_ary:
        if len(temp_str) + len(word) + 1 > 15:
            current_title.append(temp_str)
            temp_str = word
        else:
            if temp_str:
                temp_str += " " + word
            else:
                temp_str = word

    if temp_str:
        current_title.append(temp_str)

    mat_list = {}

    materials = activity.material_list.all()
    if not materials:
        mat_list["mat_1"] = "Keine Materialien"
    for i, material in enumerate(materials):
        mat_list[f"mat_{i+1}"] = material.material_name.name

    context = {
        "activity": activity,
        "title": current_title,
        "words_20_chars": words_20_chars,
        "color": color,
        **mat_list,
    }
    template = get_template(template_path)
    svg_code = template.render(context)

    png_filelike = io.BytesIO()

    if os.getenv("USE_CAIROSVG", "False") == "True":
        from cairosvg import svg2png

        svg2png(bytestring=svg_code, write_to=png_filelike)
    else:
        # Handle the case where cairosvg is not used
        # For example, you can raise an exception or use a different library
        raise NotImplementedError(
            "SVG to PNG conversion without cairosvg is not implemented."
        )

    png_filelike.seek(0)

    return FileResponse(
        png_filelike, as_attachment=True, filename=f"heimabend_der_woche_{page}.png"
    )


def download_form(request, activity_id):
    if request.method == "POST":
        form = ImageDownloadForm(request.POST)
        return redirect(
            "generate-pdf",
            activity_id=activity_id,
            color=form.data["color"],
            page=form.data["page"],
        )

    form = ImageDownloadForm()
    activity = Activity.objects.get(id=activity_id)
    return render(request, "pdf-form.html", {"form": form, "activity": activity})
