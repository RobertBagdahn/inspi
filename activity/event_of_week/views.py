# test/views.py
from django.http import FileResponse
from reportlab.pdfgen import canvas
from activity.activity.models import Activity
from django.shortcuts import redirect, render
from .forms import BookForm


def home(request):
    if request.method == "POST":
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            # Redirect to PDF generation after adding a book
            return redirect("home")
    else:
        form = BookForm()
    return render(request, "create_user_profile.html", {"form": form})


def generate_pdf(request):
    response = FileResponse(
        generate_pdf_file(request=request), as_attachment=True, filename="book_catalog.pdf"
    )
    return response


def generate_pdf_file(request):
    from io import BytesIO

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=(300, 300))

    print('request')
    print(request)

    # Create a PDF document
    activity = Activity.objects.first()

    # first page
    p.drawString(100, 200, activity.title)

    p.showPage()

    # 2nd Page
    p.drawString(200, 100, "Some text in second page.")
    p.showPage()

    # 3rd Page

    p.showPage()
    p.save()

    buffer.seek(0)
    return buffer
