from __future__ import annotations  # we use a python 3.10 Feature in line 14

from datetime import datetime
import uuid
import pytz
from django.contrib.auth import get_user_model
from django.db.models import QuerySet, Q

# from anmelde_tool.event.api_exceptions import NoUUID
from anmelde_tool.registration.models import Registration

# from basic import models as basic_models
from anmelde_tool.event import api_exceptions as event_exceptions
from anmelde_tool.event import models as event_models
from anmelde_tool.event import permissions as event_permissions

User = get_user_model()


def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


def get_bund_or_ring(ob) -> None:
    # level_id = 3
    # if not get_bund:
    #     level_id = 4
    # iterator: basic_models.ScoutHierarchy = obj
    # while iterator is not None:
    #     if iterator.level.id == level_id:
    #         return iterator
    #     iterator = iterator.parent

    return None


# def filter_registration_by_leadership(request, event_id: str, registrations: QuerySet[Registration]) \
#         -> QuerySet[Registration]:
#     event: event_models.Event = get_event(event_id)
#     user = request.user
#     leader_ship = event_permissions.check_leader_permission(event, user)
#     event_role = event_permissions.check_event_permission(event, request)
#     if event_role == event_permissions.EventRole.NONE and leader_ship != event_permissions.LeadershipRole.NONE:
#         scout_orga = get_bund_or_ring(
#             user.person.scout_group,
#             leader_ship == event_permissions.LeadershipRole.BUND_LEADER
#         )

#         if not scout_orga:
#             return Registration.objects.none()

#         registrations = registrations.filter(
#             Q(scout_organisation=scout_orga)
#             | Q(scout_organisation__parent=scout_orga)
#             | Q(scout_organisation__parent__parent=scout_orga)
#             | Q(scout_organisation__parent__parent__parent=scout_orga))
#     return registrations


# def get_event(event_id: [str, event_models.Event], ex=None) -> event_models.Event:
#     if isinstance(event_id, str):
#         if not is_valid_uuid(event_id):
#             raise NoUUID(event_id)
#         if not ex:
#             ex = event_exceptions.EventNotFound(event_id)
#         return custom_get_or_404(ex, event_models.Event, id=event_id)
#     else:
#         return event_id


# def get_registration(registration_id: [str, Registration], ex=None) -> Registration:
#     if isinstance(registration_id, str):
#         if not is_valid_uuid(registration_id):
#             raise NoUUID(registration_id)
#         if not ex:
#             ex = event_exceptions.RegistrationNotFound(registration_id)
#         return custom_get_or_404(ex, Registration, id=registration_id)
#     else:
#         return registration_id


# def custom_get_or_404(ex, model, *args, **kwargs):
#     try:
#         return model.objects.get(*args, **kwargs)
#     except model.DoesNotExist:
#         raise ex


# def to_snake_case(ordering, order_desc, ordering_fields, default_case: str = 'created_at'):
#     camel_case = ''
#     if ordering:
#         ordering = ordering.replace('.', '__')
#         camel_case = ''.join(['_' + c.lower() if c.isupper() else c for c in ordering]).lstrip('_')
#     if not ordering or camel_case not in ordering_fields:
#         camel_case = default_case
#     if order_desc:
#         camel_case = '-' + camel_case
#     return camel_case


# def age_range(min_age, max_age, participants: QuerySet[RegistrationParticipant],
#               event: event_models.Event) -> int:
#     time = event.start_date
#     max_date = datetime(time.year - min_age, time.month, time.day,
#                         tzinfo=pytz.timezone('Europe/Berlin'))
#     min_date = datetime(time.year - max_age, time.month, time.day,
#                         tzinfo=pytz.timezone('Europe/Berlin'))

#     return participants.filter(birthday__date__range=[min_date, max_date]).count()


# def get_count_by_age_gender_leader(min_age, max_age, gender, leader, participants: QuerySet[RegistrationParticipant],
#               event: event_models.Event) -> int:
#     time = event.start_date
#     max_date = datetime(time.year - min_age, time.month, time.day,
#                         tzinfo=pytz.timezone('Europe/Berlin'))
#     min_date = datetime(time.year - max_age, time.month, time.day,
#                         tzinfo=pytz.timezone('Europe/Berlin'))

#     participants = participants.filter(birthday__date__range=[min_date, max_date]).filter(gender=gender)
#     if leader == True:
#         participants = participants.exclude(leader="N")
#     else:
#         participants = participants.filter(leader="N")

#     return participants.count()


# def filter_registrations_by_query_params(request,
#                                          event_id: str,
#                                          registrations: QuerySet[Registration]) \
#         -> QuerySet[Registration]:
#     stamm_list = request.query_params.getlist('stamm')
#     ring_list = request.query_params.getlist('ring')
#     bund_list = request.query_params.getlist('bund')
#     if stamm_list:
#         registrations = registrations.filter(
#             Q(scout_organisation__id__in=stamm_list, scout_organisation__level__id=5) |
#             Q(scout_organisation__parent__id__in=stamm_list, scout_organisation__parent__level__id=5))
#     if ring_list:
#         registrations = registrations.filter(
#             Q(scout_organisation__id__in=ring_list, scout_organisation__level__id=4) |
#             Q(scout_organisation__parent__id__in=ring_list, scout_organisation__parent__level__id=4) |
#             Q(scout_organisation__parent__parent__id__in=ring_list,
#               scout_organisation__parent__parent__level__id=4))
#     if bund_list:
#         registrations = registrations.filter(
#             Q(scout_organisation__id__in=bund_list, scout_organisation__level__id=3) |
#             Q(scout_organisation__parent__id__in=bund_list, scout_organisation__parent__level__id=3) |
#             Q(scout_organisation__parent__parent__id__in=bund_list,
#               scout_organisation__parent__parent__level__id=3) |
#             Q(scout_organisation__parent__parent__parent__id__in=bund_list,
#               scout_organisation__parent__parent__parent__level__id=3))
#     registrations = filter_registration_by_leadership(request, event_id, registrations)
#     return registrations
