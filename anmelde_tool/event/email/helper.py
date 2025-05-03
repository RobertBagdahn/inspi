import html
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, render
from django.utils.translation import gettext as _
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.contrib import messages


def event_email_send_confirmation(request, registration, event):
    """
    Sends a confirmation email using the DPV base template
    """

    event_name = event.name
    
    # Prepare the context for the email template
    # Get responsible persons from registration
    responsible_persons = ""
    if hasattr(registration, 'responsible_persons') and registration.responsible_persons.exists():
        responsible_names = [person.scout_display_name for person in registration.responsible_persons.all()]
        responsible_persons = html.escape(", ".join(responsible_names))
    
    context = {
        'event_name': event_name,
        'responsible_persons': responsible_persons,
        'content_html': '<p>Hier kann indivudueller Text der Lagerleitung stehen</p>',
        'participant_count': registration.participant_count,
        'scout_organisation': registration.scout_organisation.name,
        'reg_deadline': event.registration_deadline,
        'event_url': event.get_absolute_url(),
        'registration_url': registration.get_absolute_url(),
    }
    
    # Render the email content using the DPV base template
    email_content = render_to_string('email_template/dpv/base.html', context)

    subject = f"Anmeldung für {event_name} - Bestätigung"
    from_email = 'inspirator.testmail@gmail.com'
    recipient_list=['robertbaggi@gmail.com', 'muck@dpvonline.de']
    
    # Use the existing send_custom_mail function if appropriate
    # Alternatively, use Django's built-in email functionality
    send_mail(
        subject=subject,
        message=strip_tags(email_content),  # Plain text version
        html_message=email_content,
        from_email=from_email,
        recipient_list=recipient_list,
        fail_silently=False,
    )

    return True