from django.shortcuts import render

from .models import Faq


def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def faq(request):
    faq = Faq.objects.all()
    return render(request, 'faq.html', {'faq': faq})

def impressum(request):
    return render(request, 'impressum.html')

def privacy(request):
    return render(request, 'privacy.html')

def support(request):
    return render(request, 'support.html') 
