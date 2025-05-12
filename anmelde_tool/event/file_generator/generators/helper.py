import datetime

from dateutil.relativedelta import relativedelta
from django.db.models import QuerySet

from anmelde_tool.event import models as event_models
from anmelde_tool.event.file_generator.models import GeneratedFiles
from anmelde_tool.registration.models import Registration


def get_registrations(event: event_models.Event) -> QuerySet[Registration]:
    return Registration.objects.filter(event=event)


def get_event_location(event: event_models.Event) -> str:
    if event.location:
        return f'{event.location.address}, {event.location.zip_code.zip_code} {event.location.zip_code.city}'
    else:
        return ''


def get_event_date(event: event_models.Event) -> str:
    if event.start_date and event.end_date:
        return f'{event.start_date.date().strftime("%d.%m.%Y")} - {event.end_date.date().strftime("%d.%m.%Y")}'
    else:
        return ''


def get_event_days(event: event_models.Event) -> str:
    if event.end_date and event.start_date:
        return str((event.end_date.date() - event.start_date.date()).days + 1)
    else:
        return ''


def get_event_short_description(event: event_models.Event) -> str:
    if event.short_description:
        return event.short_description
    else:
        return ''



def get_registration_scout_organisation_name(registration: Registration) -> str:
    if registration.scout_organisation:
        return registration.scout_organisation.name
    else:
        return ''


def get_booking_options_name(event: event_models.Event):
    return list(event.bookingoption_set.exclude(name__contains='Tagesgast').values_list('name', flat=True))


def get_formatted_booking_option(registration: Registration, booking_options_name: str):
    return 0


def get_current_year() -> str:
    return str(datetime.date.today().year)


def get_bund_name(file: GeneratedFiles) -> str:
    result = []
    if file and file.bund and file.bund.level == 3:
        if file.bund.abbreviation:
            result.append(file.bund.abbreviation)
        if file.bund.full_name:
            result.append(file.bund.full_name)
        return ' - '.join(result)
    return ''
