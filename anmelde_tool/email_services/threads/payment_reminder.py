import html
from datetime import timedelta

from django.core.mail import EmailMultiAlternatives
from django.template.context import make_context

from anmelde_tool.email_services.choices import EmailType
from anmelde_tool.email_services.threads.helper import get_email, get_headers, get_booking_options, get_scout_organisation_text, \
    get_event_pronoun
from anmelde_tool.event import models as event_models
from anmelde_tool.registration.models import Registration



# @shared_task
# def payment_reminder_mail(evend_id: str, email_type: EmailType):
#     event: event_models.Event = get_object_or_404(event_models.Event, id=evend_id)

#     technical_name = event.technical_name or 'info'
#     sender = f'{event.name} <{technical_name}@{getattr(settings, "EMAIL_HOST_USER")}>'
#     subject = f'Zahlungserinnerung für: {event.name}'

#     template_html, template_plain = get_email(email_type, event)

#     event_name = html.escape(event.name)
#     event_pronoun = get_event_pronoun(event_name)
#     payment_deadline = event.registration_deadline.date() + timedelta(days=3)

#     for registration in event.registration_set.all():
#         serializer = RegistrationCashSummarySerializer(registration)
#         booking_options = get_booking_options(serializer.data['booking_options'])
#         scout_organisation = get_scout_organisation_text(registration)

#         if serializer.data['payment']['open'] <= 0:
#             continue

#         for person in registration.responsible_persons.all():
#             if person.email is None or len(person.email) == 0:
#                 continue

#             receiver = [person.email, ]

#             data = {
#                 # 'responsible_persons': html.escape(person.userextended.scout_name) or '',
#                 # 'unsubscribe': person.userextended.id,
#                 'participant_count': serializer.data['participant_count'],
#                 'booking_options': booking_options,
#                 'sum': serializer.data['payment']['price'],
#                 'received_sum': serializer.data['payment']['paid'],
#                 'open_sum': serializer.data['payment']['open'],
#                 'payment_id': serializer.data['ref_id'],
#                 'scout_organisation': scout_organisation,
#                 'event_name': event_name,
#                 'event_pronoun': event_pronoun,
#                 'payment_deadline': payment_deadline
#             }

#             headers = get_headers(person, sender)

#             html_rendered = template_html.render(make_context(data, autoescape=False))
#             plain_rendered = template_plain.render(make_context(data, autoescape=False))

#             email = EmailMultiAlternatives(subject=subject,
#                                            body=plain_rendered,
#                                            from_email=sender,
#                                            to=receiver,
#                                            headers=headers,
#                                            reply_to=[sender, ])
#             email.attach_alternative(html_rendered, "text/html")
#             email.send(fail_silently=False)

# @shared_task
# def single_payment_reminder_mail(registration_id: str, email_type: EmailType):
#     registration: Registration = get_object_or_404(Registration, id=registration_id)
#     event: event_models.Event = get_object_or_404(event_models.Event, id=registration.event.id)

#     technical_name = event.technical_name or 'info'
#     sender = f'{event.name} <{technical_name}@{getattr(settings, "EMAIL_HOST_USER")}>'
#     subject = f'Zahlungserinnerung für: {event.name}'

#     template_html, template_plain = get_email(email_type, event)

#     event_name = html.escape(event.name)
#     event_pronoun = get_event_pronoun(event_name)
#     payment_deadline = event.registration_deadline.date() + timedelta(days=3)

#     serializer = RegistrationCashSummarySerializer(registration)
#     booking_options = get_booking_options(serializer.data['booking_options'])
#     scout_organisation = get_scout_organisation_text(registration)

#     if serializer.data['payment']['open'] <= 0:
#         return

#     for person in registration.responsible_persons.all():
#         if person.email is None or len(person.email) == 0:
#             continue

#         receiver = [person.email, ]

#         data = {
#             # 'responsible_persons': html.escape(person.scout_name) or '',
#             # 'unsubscribe': person.id,
#             'participant_count': serializer.data['participant_count'],
#             'booking_options': booking_options,
#             'sum': serializer.data['payment']['price'],
#             'received_sum': serializer.data['payment']['paid'],
#             'open_sum': serializer.data['payment']['open'],
#             'payment_id': serializer.data['ref_id'],
#             'scout_organisation': scout_organisation,
#             'event_name': event_name,
#             'event_pronoun': event_pronoun,
#             'payment_deadline': payment_deadline
#         }

#         headers = get_headers(person, sender)

#         html_rendered = template_html.render(make_context(data, autoescape=False))
#         plain_rendered = template_plain.render(make_context(data, autoescape=False))

#         email = EmailMultiAlternatives(subject=subject,
#                                         body=plain_rendered,
#                                         from_email=sender,
#                                         to=receiver,
#                                         headers=headers,
#                                         reply_to=[sender, ])
#         email.attach_alternative(html_rendered, "text/html")
#         email.send(fail_silently=False)
