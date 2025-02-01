from django.shortcuts import render

from .models import Faq, MessageType, Message
from .forms import MessageForm, FaqQuestionForm


def about(request):
    return render(request, 'about.html')

def contact(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'contact.html', {'form': form, 'success': True})
    else:
        form = MessageForm()
    return render(request, 'contact.html', {'form': form})

def faq(request):
    faqs = Faq.objects.all().order_by('sorting')
    context = {
        'faqs': faqs,
    }
    return render(request, 'faq.html', context)

def impressum(request):
    return render(request, 'impressum.html')

def privacy(request):
    return render(request, 'privacy.html')

def support(request):
    return render(request, 'support.html') 

def internetnacht(request):
    return render(request, 'internetnacht.html')
