# import django_filters
# from django.contrib.auth import get_user_model
# from django.db.models import QuerySet, Q
# from dateutil.relativedelta import relativedelta
# from django_filters import BaseInFilter, CharFilter
# from django.db.models import Prefetch, Sum
# from django.utils import timezone
# import decimal

# from anmelde_tool.attributes.models import (
#     BooleanAttribute,
#     IntegerAttribute,
#     FloatAttribute,
#     StringAttribute,
#     DateTimeAttribute,
#     TravelAttribute,
# )
# from anmelde_tool.event import models as event_models
# from anmelde_tool.event import permissions as event_permissions
# from anmelde_tool.event.helper import (
#     filter_registration_by_leadership,
#     get_bund_or_ring,
#     to_snake_case,
#     get_event,
#     age_range,
#     filter_registrations_by_query_params,
#     get_count_by_age_gender_leader,
# )
# from anmelde_tool.event.basic.models import EventModule
# from anmelde_tool.event.summary import serializers as summary_serializers
# from anmelde_tool.registration import models as registration_models
# from anmelde_tool.registration.models import RegistrationParticipant, Registration
# from masterdata.models import ScoutHierarchy

# from food.service.norm_person import NormPerson

# User = get_user_model()


# class WorkshopEventSummaryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
#     permission_classes = [
#         event_permissions.IsSubEventResponsiblePerson | event_permissions.IsLeaderPerson
#     ]
#     serializer_class = summary_serializers.WorkshopEventSummarySerializer

#     def get_queryset(self) -> QuerySet:
#         event_id = self.kwargs.get("event_pk", None)
#         event: event_models.Event = get_event(event_id)

#         workshops = event_models.Workshop.objects.filter(
#             registration__event__id=event_id
#         )

#         leader_ship = event_permissions.check_leader_permission(
#             event, self.request.user
#         )
#         event_role = event_permissions.check_event_permission(event, self.request)
#         if (
#             event_role == event_permissions.EventRole.NONE
#             and leader_ship != event_permissions.LeadershipRole.NONE
#         ):
#             orga = get_bund_or_ring(
#                 self.request.user.userextended.scout_organisation,
#                 leader_ship == event_permissions.LeadershipRole.BUND_LEADER,
#             )
#             workshops = workshops.filter(
#                 Q(registration__scout_organisation__parent=orga)
#                 | Q(registration__scout_organisation__parent__parent=orga)
#                 | Q(registration__scout_organisation__parent__parent__parent=orga)
#                 | Q(
#                     registration__scout_organisation__parent__parent__parent__parent=orga
#                 )
#             )
#         return workshops


# class StandardResultsSetPagination(PageNumberPagination):
#     page_size_query_param = "page-size"
#     max_page_size = 1000
#     page_size = 1000


# class LimitedResultsSetPagination(PageNumberPagination):
#     page_size_query_param = "page-size"
#     max_page_size = 50
#     page_size = 50


# class CharInFilter(BaseInFilter, CharFilter):
#     pass


# class EventSummaryFilter(django_filters.FilterSet):
#     scout_organisations = CharInFilter(
#         lookup_expr="exact", field_name="scout_organisation__name"
#     )

#     class Meta:
#         model = Registration
#         fields = ["scout_organisation"]


# class EventSummaryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
#     pagination_class = LimitedResultsSetPagination
#     permission_classes = [
#         event_permissions.IsSubEventResponsiblePerson | event_permissions.IsLeaderPerson
#     ]
#     serializer_class = summary_serializers.RegistrationEventSummarySerializer
#     ordering_fields = (
#         "scout_organisation__name",
#         "is_confirmed",
#         "created_at",
#         "-created_at",
#         "updated_at",
#     )
#     filter_backends = [DjangoFilterBackend, SearchFilter]
#     search_fields = [
#         "scout_organisation__name",
#         "responsible_persons__first_name",
#         "responsible_persons__last_name",
#         "responsible_persons__person__scout_name",
#         "responsible_persons__person__email",
#         "responsible_persons__email",
#     ]

#     def get_queryset(self) -> QuerySet:
#         event_id = self.kwargs.get("event_pk", None)
#         registrations = Registration.objects.filter(event=event_id)

#         registrations = filter_registrations_by_query_params(
#             self.request, event_id, registrations
#         )

#         scout_organisation_list = self.request.query_params.getlist(
#             "scout-organisation"
#         )
#         if scout_organisation_list:
#             registrations = registrations.filter(
#                 Q(scout_organisation__id__in=scout_organisation_list)
#                 | Q(scout_organisation__parent__id__in=scout_organisation_list)
#                 | Q(scout_organisation__parent__parent__id__in=scout_organisation_list)
#                 | Q(
#                     scout_organisation__parent__parent__parent__id__in=scout_organisation_list
#                 )
#             )

#         ordering: str = self.request.query_params.get("ordering", None)
#         order_desc: bool = (
#             self.request.query_params.get("order-desc", "false") == "true"
#         )
#         camel_case = to_snake_case(ordering, order_desc, self.ordering_fields)

#         return registrations.order_by(camel_case)


# class RegistrationLocationViewSet(EventSummaryViewSet):
#     pagination_class = None
#     serializer_class = summary_serializers.RegistrationLocationSerializer


# class EventLocationViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
#     permission_classes = [
#         event_permissions.IsSubEventResponsiblePerson | event_permissions.IsLeaderPerson
#     ]
#     serializer_class = summary_serializers.EventLocationSummarySerializer

#     def get_queryset(self) -> QuerySet:
#         event_id = self.kwargs.get("event_pk", None)
#         return event_models.Event.objects.filter(id=event_id)


# class EventDetailedSummaryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
#     permission_classes = [
#         event_permissions.IsSubEventSuperResponsiblePerson
#         | event_permissions.IsLeaderPerson
#     ]
#     serializer_class = (
#         summary_serializers.RegistrationParticipantEventDetailedSummarySerializer
#     )
#     ordering_fields = (
#         "first_name",
#         "last_name",
#         "scout_name",
#         "birthday",
#         "-birthday",
#         "scout_organisation",
#         "created_at",
#         "-created_at",
#     )
#     pagination_class = LimitedResultsSetPagination
#     filter_backends = [DjangoFilterBackend, SearchFilter]
#     filterset_fields = ["booking_option__id", "eat_habit__id"]
#     search_fields = [
#         "first_name",
#         "last_name",
#         "scout_name",
#         "booking_option__name",
#         "registration__scout_organisation__name",
#     ]

#     def get_queryset(self) -> QuerySet:
#         event_id = self.kwargs.get("event_pk", None)
#         registrations = Registration.objects.filter(event=event_id)
#         registrations = filter_registrations_by_query_params(
#             self.request, event_id, registrations
#         )

#         reg_ids = registrations.values_list("id", flat=True)

#         participants: QuerySet = RegistrationParticipant.objects.filter(
#             registration__id__in=reg_ids
#         )

#         booking_option_list = self.request.query_params.getlist("booking-option")
#         if booking_option_list:
#             participants = participants.filter(booking_option__in=booking_option_list)

#         scout_organisation_list = self.request.query_params.getlist(
#             "scout-organisation"
#         )
#         if scout_organisation_list:
#             regs = registrations.filter(
#                 Q(scout_organisation__id__in=scout_organisation_list)
#                 | Q(scout_organisation__parent__id__in=scout_organisation_list)
#                 | Q(scout_organisation__parent__parent__id__in=scout_organisation_list)
#                 | Q(
#                     scout_organisation__parent__parent__parent__id__in=scout_organisation_list
#                 )
#             )
#             participants = participants.filter(registration__in=regs)

#         ordering: str = self.request.query_params.get("ordering", None)
#         order_desc: bool = (
#             self.request.query_params.get("order-desc", "false") == "true"
#         )
#         camel_case = to_snake_case(
#             ordering, order_desc, self.ordering_fields, "last_name"
#         )

#         check_case = ("-" if order_desc else "") + "scout_organisation"
#         if camel_case == check_case:
#             camel_case = (
#                 "-" if order_desc else ""
#             ) + "registration__scout_organisation__name"

#         return participants.order_by(camel_case)


# class EventModuleSummaryViewSet(viewsets.ReadOnlyModelViewSet):
#     permission_classes = [
#         event_permissions.IsSubEventResponsiblePerson | event_permissions.IsLeaderPerson
#     ]
#     serializer_class = EventModuleSummarySerializer

#     def get_queryset(self):
#         event_id = self.kwargs.get("event_pk", None)
#         return EventModule.objects.filter(event__id=event_id).exclude(
#             name__in=["Participants", "Introduction", "Summary"]
#         )


# class EventFoodSummaryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
#     permission_classes = [
#         event_permissions.IsSubEventResponsiblePerson | event_permissions.IsLeaderPerson
#     ]

#     def list(self, request, *args, **kwargs) -> Response:
#         participants: QuerySet[RegistrationParticipant] = self.get_queryset()

#         eat_habits_sum = {}
#         eat_habits = {}
#         for participant in participants.all():
#             key = tuple(participant.eat_habit.values_list("id", flat=True))
#             if key in eat_habits_sum:
#                 eat_habits_sum[key] += 1
#             else:
#                 eat_habits_sum[key] = 1
#                 eat_habits[key] = participant.eat_habit.all()

#         formatted_eat_habits = []
#         for key in eat_habits:
#             food = ", ".join(eat_habits[key].values_list("name", flat=True))
#             if food is None or food == "":
#                 food = "Normal"
#             result = {
#                 "sum": eat_habits_sum[key],
#                 "food": food,
#             }
#             formatted_eat_habits.append(result)

#         norm_persons_low = 0
#         norm_persons_high = 0
#         norm_person_count = 0
#         for participant in participants.all():

#             age = relativedelta(timezone.now(), participant.birthday).years
#             norm_persons_low += NormPerson().get_norm_person(
#                 participant.gender, age, 1.3
#             )
#             norm_persons_high += NormPerson().get_norm_person(
#                 participant.gender, age, 1.7
#             )
#             norm_person_count += 1

#         result = {
#             "eat_habits": formatted_eat_habits,
#             "norm_persons": {
#                 "low": norm_persons_low,
#                 "high": norm_persons_high,
#                 "count": norm_person_count,
#             },
#         }

#         return Response(result, status=status.HTTP_200_OK)

#     def get_queryset(self) -> QuerySet[RegistrationParticipant]:
#         event_id = self.kwargs.get("event_pk", None)

#         registrations = Registration.objects.filter(event=event_id)
#         registrations = filter_registrations_by_query_params(
#             self.request, event_id, registrations
#         )

#         registration_ids = registrations.values_list("id", flat=True)

#         queryset = RegistrationParticipant.objects.filter(
#             registration__id__in=registration_ids
#         )

#         booking_option_list = self.request.query_params.getlist("booking-option")
#         if booking_option_list:
#             queryset = queryset.filter(booking_option__in=booking_option_list)

#         registration = self.request.query_params.get("regId", None)
#         if registration:
#             queryset = queryset.filter(registration=registration)

#         return queryset


# class EventLeaderTypesSummaryViewSet(EventFoodSummaryViewSet):
#     def list(self, request, *args, **kwargs) -> Response:
#         all_participants: QuerySet[RegistrationParticipant] = self.get_queryset()

#         n = self.get_leder_type_count("N", all_participants)
#         staFue = self.get_leder_type_count("StaFue", all_participants)
#         siFue = self.get_leder_type_count("SiFue", all_participants)
#         roFue = self.get_leder_type_count("RoFue", all_participants)
#         meuFue = self.get_leder_type_count("MeuFue", all_participants)

#         result = {
#             "n": n,
#             "staFue": staFue,
#             "siFue": siFue,
#             "roFue": roFue,
#             "meuFue": meuFue,
#         }

#         return Response(result, status=status.HTTP_200_OK)

#     def get_leder_type_count(
#         self, leader_type, participants: QuerySet[RegistrationParticipant]
#     ):
#         return participants.filter(leader=leader_type).count()


# class EventAgeGroupsSummaryViewSet(EventFoodSummaryViewSet):
#     def list(self, request, *args, **kwargs) -> Response:
#         """
#         0-10 Wölfling
#         11-16 Pfadfinder
#         17-23 Rover
#         23+ Altrover
#         """
#         event_id = self.kwargs.get("event_pk", None)
#         event = get_event(event_id)
#         all_participants: QuerySet[RegistrationParticipant] = self.get_queryset()

#         registration = self.request.query_params.get("regId", None)
#         if registration:
#             all_participants = all_participants.filter(registration=registration)

#         woelfling = age_range(0, 11, all_participants, event)
#         pfadfinder = age_range(11, 16, all_participants, event)
#         rover = age_range(16, 25, all_participants, event)
#         alt_rover = age_range(25, 999, all_participants, event)

#         result = {
#             "woelfling": woelfling,
#             "pfadfinder": pfadfinder,
#             "rover": rover,
#             "alt_rover": alt_rover,
#         }

#         return Response(result, status=status.HTTP_200_OK)


# class EventAgeGroupsSummaryDetailViewSet(EventFoodSummaryViewSet):
#     def list(self, request, *args, **kwargs) -> Response:
#         """
#         0-10 Wölfling
#         11-16 Pfadfinder
#         17-23 Rover
#         23+ Altrover
#         """
#         event_id = self.kwargs.get("event_pk", None)
#         event = get_event(event_id)
#         all_participants: QuerySet[RegistrationParticipant] = self.get_queryset()

#         result = {
#             "p_6-_m_no": get_count_by_age_gender_leader(
#                 0, 7, "M", False, all_participants, event
#             ),
#             "p_07_m_no": get_count_by_age_gender_leader(
#                 7, 8, "M", False, all_participants, event
#             ),
#             "p_08_m_no": get_count_by_age_gender_leader(
#                 8, 9, "M", False, all_participants, event
#             ),
#             "p_09_m_no": get_count_by_age_gender_leader(
#                 9, 10, "M", False, all_participants, event
#             ),
#             "p_10_m_no": get_count_by_age_gender_leader(
#                 10, 11, "M", False, all_participants, event
#             ),
#             "p_11_m_no": get_count_by_age_gender_leader(
#                 11, 12, "M", False, all_participants, event
#             ),
#             "p_12_m_no": get_count_by_age_gender_leader(
#                 12, 13, "M", False, all_participants, event
#             ),
#             "p_13_m_no": get_count_by_age_gender_leader(
#                 13, 14, "M", False, all_participants, event
#             ),
#             "p_14_m_no": get_count_by_age_gender_leader(
#                 14, 15, "M", False, all_participants, event
#             ),
#             "p_15_m_no": get_count_by_age_gender_leader(
#                 15, 16, "M", False, all_participants, event
#             ),
#             "p_16_m_no": get_count_by_age_gender_leader(
#                 16, 17, "M", False, all_participants, event
#             ),
#             "p_17_m_no": get_count_by_age_gender_leader(
#                 17, 18, "M", False, all_participants, event
#             ),
#             "p_18_m_no": get_count_by_age_gender_leader(
#                 18, 19, "M", False, all_participants, event
#             ),
#             "p_19_m_no": get_count_by_age_gender_leader(
#                 19, 20, "M", False, all_participants, event
#             ),
#             "p_20_m_no": get_count_by_age_gender_leader(
#                 20, 21, "M", False, all_participants, event
#             ),
#             "p_21_m_no": get_count_by_age_gender_leader(
#                 21, 22, "M", False, all_participants, event
#             ),
#             "p_22_m_no": get_count_by_age_gender_leader(
#                 22, 23, "M", False, all_participants, event
#             ),
#             "p_23_m_no": get_count_by_age_gender_leader(
#                 23, 24, "M", False, all_participants, event
#             ),
#             "p_24_m_no": get_count_by_age_gender_leader(
#                 24, 25, "M", False, all_participants, event
#             ),
#             "p_25_m_no": get_count_by_age_gender_leader(
#                 25, 26, "M", False, all_participants, event
#             ),
#             "p_26_m_no": get_count_by_age_gender_leader(
#                 26, 27, "M", False, all_participants, event
#             ),
#             "p_26+_m_no": get_count_by_age_gender_leader(
#                 27, 100, "M", False, all_participants, event
#             ),
#             "p_6-_f_no": get_count_by_age_gender_leader(
#                 0, 7, "F", False, all_participants, event
#             ),
#             "p_07_f_no": get_count_by_age_gender_leader(
#                 7, 8, "F", False, all_participants, event
#             ),
#             "p_08_f_no": get_count_by_age_gender_leader(
#                 8, 9, "F", False, all_participants, event
#             ),
#             "p_09_f_no": get_count_by_age_gender_leader(
#                 9, 10, "F", False, all_participants, event
#             ),
#             "p_10_f_no": get_count_by_age_gender_leader(
#                 10, 11, "F", False, all_participants, event
#             ),
#             "p_11_f_no": get_count_by_age_gender_leader(
#                 11, 12, "F", False, all_participants, event
#             ),
#             "p_12_f_no": get_count_by_age_gender_leader(
#                 12, 13, "F", False, all_participants, event
#             ),
#             "p_13_f_no": get_count_by_age_gender_leader(
#                 13, 14, "F", False, all_participants, event
#             ),
#             "p_14_f_no": get_count_by_age_gender_leader(
#                 14, 15, "F", False, all_participants, event
#             ),
#             "p_15_f_no": get_count_by_age_gender_leader(
#                 15, 16, "F", False, all_participants, event
#             ),
#             "p_16_f_no": get_count_by_age_gender_leader(
#                 16, 17, "F", False, all_participants, event
#             ),
#             "p_17_f_no": get_count_by_age_gender_leader(
#                 17, 18, "F", False, all_participants, event
#             ),
#             "p_18_f_no": get_count_by_age_gender_leader(
#                 18, 19, "F", False, all_participants, event
#             ),
#             "p_19_f_no": get_count_by_age_gender_leader(
#                 19, 20, "F", False, all_participants, event
#             ),
#             "p_20_f_no": get_count_by_age_gender_leader(
#                 20, 21, "F", False, all_participants, event
#             ),
#             "p_21_f_no": get_count_by_age_gender_leader(
#                 21, 22, "F", False, all_participants, event
#             ),
#             "p_22_f_no": get_count_by_age_gender_leader(
#                 22, 23, "F", False, all_participants, event
#             ),
#             "p_23_f_no": get_count_by_age_gender_leader(
#                 23, 24, "F", False, all_participants, event
#             ),
#             "p_24_f_no": get_count_by_age_gender_leader(
#                 24, 25, "F", False, all_participants, event
#             ),
#             "p_25_f_no": get_count_by_age_gender_leader(
#                 25, 26, "F", False, all_participants, event
#             ),
#             "p_26_f_no": get_count_by_age_gender_leader(
#                 26, 27, "F", False, all_participants, event
#             ),
#             "p_26+_f_no": get_count_by_age_gender_leader(
#                 27, 1000, "F", False, all_participants, event
#             ),
#             "p_16-_m_yes": get_count_by_age_gender_leader(
#                 1, 16, "M", True, all_participants, event
#             ),
#             "p_16-_f_yes": get_count_by_age_gender_leader(
#                 1, 16, "F", True, all_participants, event
#             ),
#             "p_16-17_m_yes": get_count_by_age_gender_leader(
#                 16, 17, "M", True, all_participants, event
#             ),
#             "p_16-17_f_yes": get_count_by_age_gender_leader(
#                 16, 17, "F", True, all_participants, event
#             ),
#             "p_18-26_m_yes": get_count_by_age_gender_leader(
#                 18, 26, "M", True, all_participants, event
#             ),
#             "p_18-26_f_yes": get_count_by_age_gender_leader(
#                 18, 26, "F", True, all_participants, event
#             ),
#             "p_27-44_m_yes": get_count_by_age_gender_leader(
#                 27, 44, "M", True, all_participants, event
#             ),
#             "p_27-44_f_yes": get_count_by_age_gender_leader(
#                 27, 44, "F", True, all_participants, event
#             ),
#             "p_45+_m_yes": get_count_by_age_gender_leader(
#                 45, 1000, "M", True, all_participants, event
#             ),
#             "p_45+_f_yes": get_count_by_age_gender_leader(
#                 45, 1000, "F", True, all_participants, event
#             ),
#         }

#         return Response(result, status=status.HTTP_200_OK)


# class EventAlcoholAgeGroupsSummaryViewSet(EventFoodSummaryViewSet):
#     def list(self, request, *args, **kwargs) -> Response:
#         event_id = self.kwargs.get("event_pk", None)
#         event = get_event(event_id)
#         all_participants: QuerySet[RegistrationParticipant] = self.get_queryset()

#         young = age_range(0, 16, all_participants, event)
#         teen = age_range(16, 18, all_participants, event)
#         adult = age_range(18, 999, all_participants, event)

#         result = {"child": young, "teen": teen, "adult": adult}

#         return Response(result, status=status.HTTP_200_OK)


# class CashSummaryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
#     def list(self, request, *args, **kwargs) -> Response:
#         registrations: QuerySet[Registration] = self.get_queryset()
#         event_id = self.kwargs.get("event_pk", None)
#         registrations = filter_registration_by_leadership(
#             request, event_id, registrations
#         )
#         total = registrations.aggregate(
#             sum=Sum("registrationparticipant__booking_option__price")
#         )["sum"]
#         paid = registrations.aggregate(sum=Sum("cashincome__amount"))["sum"]
#         if total:
#             total = float(total)
#         else:
#             total = float(0.0)

#         if paid:
#             paid = float(paid)
#         else:
#             paid = float(0.0)

#         unpaid = total - paid
#         result = {"total": total, "paid": paid, "unpaid": unpaid}

#         return Response(result, status=status.HTTP_200_OK)

#     def get_queryset(self) -> QuerySet[registration_models.Registration]:
#         event_id = self.kwargs.get("event_pk", None)
#         return registration_models.Registration.objects.filter(event_id=event_id)


# class CashSummaryListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
#     permission_classes = [
#         event_permissions.IsSubEventResponsiblePerson | event_permissions.IsLeaderPerson
#     ]
#     serializer_class = summary_serializers.RegistrationCashSummarySerializer

#     def list(self, request, *args, **kwargs) -> Response:
#         registrations: QuerySet[Registration] = self.get_queryset()
#         serializer = summary_serializers.RegistrationCashSummarySerializer(
#             registrations, many=True, read_only=True
#         )

#         returnData = []
#         paid = request.GET.get("paid", None)

#         if paid is not None:
#             for item in serializer.data:
#                 if item["payment"].get("open") <= 0 and (paid == "true"):
#                     returnData.append(item)
#                 if item["payment"].get("open") > 0 and (paid == "false"):
#                     returnData.append(item)
#         else:
#             returnData = serializer.data

#         return Response(returnData, status=status.HTTP_200_OK)

#     def get_queryset(self) -> QuerySet[registration_models.Registration]:
#         event_id = self.kwargs.get("event_pk", None)
#         search = self.request.query_params.get("search", None)

#         registrations = registration_models.Registration.objects.filter(
#             event_id=event_id
#         )

#         if search:
#             registrations = registrations.filter(
#                 scout_organisation__name__icontains=search
#             )

#         registrations = filter_registration_by_leadership(
#             request=self.request, event_id=event_id, registrations=registrations
#         )
#         return registrations.order_by("scout_organisation__name")


# class CashDetailViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
#     permission_classes = [event_permissions.IsSubRegistrationResponsiblePerson]
#     serializer_class = summary_serializers.RegistrationCashSummarySerializer

#     def get_queryset(self) -> QuerySet[registration_models.Registration]:
#         registration_id = self.kwargs.get("registration_pk", None)
#         return registration_models.Registration.objects.filter(id=registration_id)


# class EmailResponsiblePersonsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
#     permission_classes = [event_permissions.IsSubEventResponsiblePerson]
#     serializer_class = summary_serializers.UserEmailSerializer

#     def get_queryset(self) -> QuerySet[User]:
#         event_id = self.kwargs.get("event_pk", None)
#         only_admin = self.request.query_params.get("only-admins", False)
#         event: event_models.Event = event_models.Event.objects.filter(
#             id=event_id
#         ).first()

#         all_users: QuerySet[User] = event.responsible_persons.exclude(email__exact="")

#         if event.keycloak_admin_path:
#             admin_groups: QuerySet[User] = event.keycloak_admin_path.user_set.exclude(
#                 email__exact=""
#             )
#             all_users = admin_groups | all_users

#         if not only_admin and event.keycloak_path:
#             normal_groups: QuerySet[User] = event.keycloak_path.user_set.exclude(
#                 email__exact=""
#             )
#             all_users = all_users | normal_groups

#         return all_users.distinct()


# class EmailRegistrationResponsiblePersonsViewSet(
#     mixins.ListModelMixin, viewsets.GenericViewSet
# ):
#     permission_classes = [event_permissions.IsSubEventResponsiblePerson]
#     serializer_class = summary_serializers.UserEmailSerializer

#     def get_queryset(self) -> QuerySet[User]:
#         event_id = self.kwargs.get("event_pk", None)

#         confirmed: bool = self.request.query_params.get("confirmed", "true") == "true"
#         unconfirmed: bool = (
#             self.request.query_params.get("unconfirmed", "true") == "true"
#         )
#         # all_participants: bool = self.request.query_params.get('all-participants', False)

#         all_registrations: QuerySet[Registration] = Registration.objects.filter(
#             event=event_id
#         )
#         registrations: QuerySet[Registration] = Registration.objects.none()

#         if confirmed:
#             confirmed_registrations = all_registrations.filter(is_confirmed=True)
#             registrations = registrations | confirmed_registrations

#         if unconfirmed:
#             unconfirmed_registrations = all_registrations.filter(is_confirmed=False)
#             registrations = registrations | unconfirmed_registrations

#         registrations_ids: QuerySet[int] = (
#             registrations.all()
#             .distinct()
#             .values_list("responsible_persons__id", flat=True)
#         )
#         all_users = (
#             User.objects.filter(id__in=registrations_ids)
#             .distinct()
#             .exclude(email__exact="")
#         )

#         return all_users


# class RegistrationParentViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
#     permission_classes = [
#         event_permissions.IsSubEventResponsiblePerson | event_permissions.IsLeaderPerson
#     ]
#     serializer_class = ScoutHierarchySerializer

#     def get_queryset(self):
#         event_id = self.kwargs.get("event_pk", None)
#         level_id = self.request.query_params.get("level", 5)

#         registrations = Registration.objects.filter(event=event_id)
#         registrations = filter_registration_by_leadership(
#             self.request, event_id, registrations
#         )
#         ids = registrations.values_list("scout_organisation__id", flat=True)

#         return (
#             ScoutHierarchy.objects.filter(
#                 Q(id__in=ids)
#                 | Q(parent__id__in=ids)
#                 | Q(parent__parent__id__in=ids)
#                 | Q(parent__parent__parent__id__in=ids),
#                 level__id=level_id,
#             )
#             .distinct()
#             .order_by("name")
#         )


# class MergeRegistrationsViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
#     permission_classes = [
#         event_permissions.IsSubEventResponsiblePerson | event_permissions.IsLeaderPerson
#     ]

#     def create(self, request, *args, **kwargs):
#         data = request.data

#         reg_id_primary = data["reg_primary"]
#         reg_id_secondary = data["reg_secondary"]
#         reg_primary = Registration.objects.get(id=reg_id_primary)
#         reg_secondary = Registration.objects.get(id=reg_id_secondary)

#         model_list = [
#             RegistrationParticipant,
#             BooleanAttribute,
#             IntegerAttribute,
#             FloatAttribute,
#             StringAttribute,
#             DateTimeAttribute,
#             TravelAttribute,
#         ]

#         for model in model_list:
#             # move all items from secondary to primary
#             secondary_list = model.objects.filter(registration=reg_id_secondary)
#             secondary_list.update(registration=reg_id_primary)

#         # copy responsible persons from secondary to primary
#         if data["copy_responsible_persons"]:
#             reg_primary.responsible_persons.add(
#                 *reg_secondary.responsible_persons.all()
#             )

#         # delete secondary registration
#         if data["delete_secondary"]:
#             reg_secondary.delete()

#         return Response({"id": reg_primary.event.id}, status=status.HTTP_200_OK)
