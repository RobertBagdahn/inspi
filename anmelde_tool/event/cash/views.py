
# from anmelde_tool.email_services.services import send_payment_reminder_mail, send_single_payment_reminder_mail
# from anmelde_tool.event.cash import permissions as cash_permissions
# from anmelde_tool.event import permissions as event_permissions
# from anmelde_tool.event.cash import serializers as cash_serializers
# from anmelde_tool.event.cash import models as cash_models


# class CashIncomeViewSet(viewsets.ModelViewSet):
#     permission_classes = [cash_permissions.IsCashResponsiblePerson]
#     serializer_class = cash_serializers.CashIncomeSerializer
#     queryset = cash_models.CashIncome.objects.all()

#     def create(self, request, *args, **kwargs):
#         request.data["transfer_person"] = request.user.id

#         request.data["amount"] = float(request.data["amount"].replace(",", "."))
#         return super().create(request, *args, **kwargs)

#     def update(self, request, *args, **kwargs):
#         request.data["amount"] = float(request.data["amount"].replace(",", "."))
#         return super().update(request, *args, **kwargs)


# class MailReminderViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
#     permission_classes = [event_permissions.IsEventSuperResponsiblePerson]
#     serializer_class = cash_serializers.MailReminderSerializer

#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         event_id = serializer.data["event_id"]
#         send_payment_reminder_mail(event_id)
#         return Response(serializer.data, status=status.HTTP_200_OK)

# class MailSingleReminderViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
#     permission_classes = [event_permissions.IsEventSuperResponsiblePerson]
#     serializer_class = cash_serializers.MailSingleReminderSerializer

#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         registration_id = serializer.data["registration_id"]
#         send_single_payment_reminder_mail(registration_id)
#         return Response(serializer.data, status=status.HTTP_200_OK)
