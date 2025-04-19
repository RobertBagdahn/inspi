
from anmelde_tool.event.cash.models import CashIncome
from anmelde_tool.event.permissions import check_event_permission, EventRole
from anmelde_tool.registration.models import Registration


# class IsCashResponsiblePerson(permissions.BasePermission):
#     message = 'Du darfst dieses Überweisung nicht bearbeiten'

#     def has_permission(self, request: Request, view) -> bool:
#         registration_id: str = request.data.get('registration', None)
#         pk: str = view.kwargs.get("pk", None)

#         if not request.user or not request.user.is_authenticated:
#             return False
#         if request.user.is_superuser:
#             return True
#         if registration_id is not None:
#             registration: Registration = get_object_or_404(Registration, id=registration_id)
#             event = registration.event
#         elif pk is not None:
#             cash_income: CashIncome = get_object_or_404(CashIncome, id=pk)
#             event = cash_income.registration.event
#         else:
#             raise Exception('Error')

#         return check_event_permission(event, request, admin_only=True) != EventRole.NONE
