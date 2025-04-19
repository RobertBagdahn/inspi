# from .choices import EmailType
# from .threads.registration import registration_confirmed_mail
# from .threads.payment_reminder import payment_reminder_mail, single_payment_reminder_mail
# from .threads.news import news_mail



# def send_registration_created_mail(**kwargs):
#     instance_id = kwargs.get('instance_id')
#     if instance_id and email_active:
#         registration_confirmed_mail.delay(instance_id, EmailType.RegistrationCreated)


# def send_payment_reminder_mail(event_id):
#     if email_active:
#         payment_reminder_mail.delay(event_id, EmailType.PaymentReminder)


# def send_single_payment_reminder_mail(registration_id):
#     if email_active:
#         single_payment_reminder_mail.delay(registration_id, EmailType.PaymentReminder)


# def send_custom_mail(event_id, data):
#     if email_active:
#         news_mail.delay(event_id, data, EmailType.StandardEmail)
