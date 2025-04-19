from django.db.models import QuerySet, Count
from django.http import JsonResponse

from anmelde_tool.event import api_exceptions
from anmelde_tool.event import permissions as event_permissions
from anmelde_tool.event.helper import filter_registration_by_leadership
from anmelde_tool.event.summary.kpi import serializers as kpi_serializers
from anmelde_tool.registration.models import Registration, RegistrationParticipant
from anmelde_tool.registration import models as registration_models
from anmelde_tool.event import models as event_models
from django.db.models import Func, Sum, F, Window


# class TotalParticipantsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
#     permission_classes = [
#         event_permissions.IsSubEventResponsiblePerson | event_permissions.IsLeaderPerson
#     ]

#     def list(self, request, *args, **kwargs) -> Response:
#         registrations: QuerySet[Registration] = self.get_queryset()
#         num = (
#             registrations.aggregate(count=Count("registrationparticipant"))["count"]
#             or 0
#         )
#         return Response(num, status=status.HTTP_200_OK)

#     def get_queryset(self) -> QuerySet[Registration]:
#         event_id = self.kwargs.get("event_pk", None)

#         registrations = Registration.objects.filter(event=event_id)
#         registrations = filter_registration_by_leadership(
#             self.request, event_id, registrations
#         )

#         return registrations


# class TotalRegistrationsViewSet(TotalParticipantsViewSet):
#     def list(self, request, *args, **kwargs) -> Response:
#         registrations: QuerySet[Registration] = self.get_queryset()
#         num = registrations.count() or 0

#         return Response(num, status=status.HTTP_200_OK)


# class LastRegistrationsViewSet(TotalParticipantsViewSet):
#     permission_classes = [
#         event_permissions.IsSubEventResponsiblePerson | event_permissions.IsLeaderPerson
#     ]

#     def list(self, request, *args, **kwargs) -> Response:
#         registrations: QuerySet[Registration] = self.get_queryset()
#         registrations = registrations.annotate(
#             count=Count("registrationparticipant")
#         ).order_by("-created_at")
#         result = registrations[:5]

#         serializer = kpi_serializers.RegistrationEventKPISerializer(
#             result, many=True, read_only=True
#         )

#         return Response(serializer.data, status=status.HTTP_200_OK)


# class LargestRegistrationsViewSet(TotalParticipantsViewSet):
#     permission_classes = [
#         event_permissions.IsSubEventResponsiblePerson | event_permissions.IsLeaderPerson
#     ]

#     def list(self, request, *args, **kwargs) -> Response:
#         registrations: QuerySet[Registration] = self.get_queryset()
#         registrations = registrations.annotate(
#             count=Count("registrationparticipant")
#         ).order_by("-count")
#         result = registrations[:5]

#         serializer = kpi_serializers.RegistrationEventKPISerializer(
#             result, many=True, read_only=True
#         )
#         return Response(serializer.data, status=status.HTTP_200_OK)


# class BookingOptionViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
#     permission_classes = [
#         event_permissions.IsSubEventResponsiblePerson | event_permissions.IsLeaderPerson
#     ]

#     def get_queryset(self) -> QuerySet:
#         event_id = self.kwargs.get("event_pk", None)
#         return event_models.BookingOption.objects.filter(event=event_id)

#     def list(self, request, *args, **kwargs) -> Response:
#         booking_options: QuerySet[
#             registration_models.BookingOption
#         ] = self.get_queryset()
#         serializer = kpi_serializers.BookingOptionKPISerializer(
#             booking_options, many=True, read_only=True
#         )

#         return Response(serializer.data, status=status.HTTP_200_OK)


# class RegistrationByDateViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
#     permission_classes = [
#         event_permissions.IsSubEventResponsiblePerson | event_permissions.IsLeaderPerson
#     ]

#     def get_queryset(self) -> QuerySet:
#         event_id = self.kwargs.get("event_pk", None)
#         return RegistrationParticipant.objects.filter(registration__event_id=event_id)

#     def list(self, request, *args, **kwargs) -> Response:
#         items: QuerySet[RegistrationParticipant] = self.get_queryset()
#         # aggregate the registrations by date and sort by date and count
#         result = (
#             items.values(
#                 "registration__scout_organisation__parent_id__name", "created_at__date"
#             )
#             .annotate(
#                 cumsum=Window(
#                     Count("id"),
#                     order_by=[
#                         F("created_at__date").asc(),
#                         F("registration__scout_organisation__parent_id__name").asc(),
#                     ],
#                 )
#             )
#             .values(
#                 "created_at__date",
#                 "cumsum",
#                 "registration__scout_organisation__parent_id__name",
#             )
#             .order_by("created_at__date", "cumsum")
#         )
#         return Response(result, status=status.HTTP_200_OK)
