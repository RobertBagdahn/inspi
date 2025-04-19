# import html

# from django.contrib.auth import get_user_model
# from django.core.mail import EmailMultiAlternatives
# from django.template.context import make_context

# from anmelde_tool.registration.models import Registration
# from anmelde_tool.email_services.choices import EmailType
# from anmelde_tool.email_services.threads.helper import get_email, get_headers, get_event_pronoun, \
#     get_html_participant_list, \
#     get_participant_count, get_scout_organisation_text
# from anmelde_tool.event import models as event_models


# @shared_task
# def registration_confirmed_mail(registration_id: str, email_type: EmailType):
#     registration: Registration = get_object_or_404(Registration, id=registration_id)
#     event: event_models.Event = registration.event

#     technical_name = event.technical_name or 'info'
#     sender = f'{event.name} <{technical_name}@{getattr(settings, "EMAIL_HOST_USER")}>'
#     subject = f'Registrierungsbestätigung für: {event.name}'

#     template_html, template_plain = get_email(email_type, event)

#     if template_html is None or template_plain is None:
#         return

#     count, participant_sum = get_participant_count(registration)

#     if count > 0:
#         list_participants = get_html_participant_list(registration)
#     else:
#         list_participants = ''

#     event_name = html.escape(event.name)
#     event_pronoun = get_event_pronoun(event_name)

#     scout_organisation = get_scout_organisation_text(registration)

#     person : User
#     for person in registration.responsible_persons.all():
#         receiver = [person.email, ]

#         data = {
#             'event_name': event_name,
#             'event_pronoun': event_pronoun,
#             'responsible_persons': html.escape(person.person.scout_name) or '',
#             'unsubscribe': person.id,
#             'participant_count': count,
#             'sum': participant_sum,
#             'list_participants': list_participants,
#             'scout_organisation': scout_organisation
#         }

#         headers = get_headers(person, sender)

#         html_rendered = template_html.render(make_context(data, autoescape=False))
#         plain_rendered = template_plain.render(make_context(data, autoescape=False))

#         email = EmailMultiAlternatives(subject=subject,
#                                        body=plain_rendered,
#                                        from_email=sender,
#                                        to=receiver,
#                                        headers=headers,
#                                        reply_to=[sender, ])
#         email.attach_alternative(html_rendered, "text/html")
#         email.send(fail_silently=False)
