# test/views.py
from django.http import FileResponse
from reportlab.pdfgen import canvas
from activity.activity.models import Activity
from django.shortcuts import redirect, render
from .forms import ImageDownloadForm
from django.template.loader import get_template

from cairosvg import svg2png


def generate_png_from_svg(request, activity_id, color, page):
    activity = Activity.objects.get(id=activity_id)

    print("generate_png_from_svg", activity_id, color, page)

    template_path = f"svg/heimabend_der_woche_{page}.svg"

    words = activity.summary.split('<br />')
    words = [item for sublist in [word.split() for word in activity.summary.split('<br />')] for item in sublist]
    
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

    print("current_title", current_title)

    context = {
        "activity": activity,
        "title": current_title,
        "words_20_chars": words_20_chars,
        "color": color,
    }
    template = get_template(template_path)
    svg_code = template.render(context)

    svg2png(bytestring=svg_code, write_to="output.png")

    return FileResponse(open("output.png", "rb"))


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
