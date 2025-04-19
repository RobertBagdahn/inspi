from enum import Enum

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

# from anmelde_tool.event.api_exceptions import RequiredGroupNotFound
# from anmelde_tool.event.helper import get_event, get_registration, custom_get_or_404
# from anmelde_tool.event.basic.models import Event
# from anmelde_tool.registration.models import Registration

# CREATE_METHOD = 'POST'
# UPDATE_METHODS = ('UPDATE', 'PATCH')

# User = get_user_model()


# class LeadershipRole(str, Enum):
#     NONE = "None",
#     RING_LEADER = "Ringführung",
#     BUND_LEADER = "Bundesführung",


# class EventRole(str, Enum):
#     NONE = None,
#     VIEW_ROLE = "View",
#     ADMIN_ROLE = "Admin",


# def get_keycloak_permission(user: User, keycloak_role: Group) -> bool:
#     return user.groups.filter(name=keycloak_role).exists()


# def get_responsible_person_permission(user: User, event: Event) -> bool:
#     return event.responsible_persons.filter(id=user.id).exists() if event.responsible_persons else False


# def check_event_permission(event_id: [str, Event], request, admin_only=False) -> EventRole:
#     user = request.user
#     if user.is_superuser:
#         return EventRole.ADMIN_ROLE
#     event = get_event(event_id)
#     token = request.META.get('HTTP_AUTHORIZATION')
#     child_ids = get_groups_of_user(token, user.keycloak_id)
#     if not admin_only and any(event.view_group.keycloak_id == child_id for child_id in child_ids):
#         return EventRole.VIEW_ROLE
#     if any(event.admin_group.keycloak_id == child_id for child_id in child_ids):
#         return EventRole.ADMIN_ROLE
#     if get_responsible_person_permission(user, event):
#         return EventRole.ADMIN_ROLE
#     return EventRole.NONE


# def check_leader_permission(event_id: [str, Event], user: User) -> LeadershipRole:
#     event: Event = get_event(event_id)
#     if event.view_allow_subgroup:
#         perm_name = 'dpv_bundesfuehrungen'
#         perm_name_dpbm = 'dpbm_ringfuehrungen'
#         if event.invited_groups.filter(name__in=["DPV"]).exists():
#             bufu_group = custom_get_or_404(RequiredGroupNotFound(perm_name), Group, name=perm_name)
#             if get_keycloak_permission(user, bufu_group):
#                 return LeadershipRole.BUND_LEADER
#         if event.invited_groups.filter(name__in=["DPBM"]).exists():
#             ring_group = Group.objects.filter(name=perm_name_dpbm).first()
#             if ring_group and get_keycloak_permission(user, ring_group):
#                 return LeadershipRole.RING_LEADER
#     return LeadershipRole.NONE


# def check_registration_permission(registration_id: str, request) -> bool:
#     registration: Registration = get_registration(registration_id)
#     return registration.responsible_persons.contains(request.user) \
#         or check_event_permission(registration.event, request, admin_only=True) != EventRole.NONE


# class IsStaffOrReadOnly(permissions.BasePermission):
#     message = 'Kann nur von den Admins bearbeitet werden'

#     def has_permission(self, request: Request, view) -> bool:
#         return bool(
#             request.method in SAFE_METHODS or
#             (request.user and request.user.is_authenticated and request.user.is_staff)
#         )


# class IsEventSuperResponsiblePerson(permissions.BasePermission):
#     message = 'Du darfst dieses Event nicht bearbeiten'

#     def has_permission(self, request: Request, view) -> bool:
#         if not request.user or not request.user.is_authenticated:
#             return False
#         if request.user.is_superuser:
#             return True
#         if request.method == CREATE_METHOD:
#             return True
#         event_id: str = view.kwargs.get("pk", None)
#         return check_event_permission(event_id, request, admin_only=True) == EventRole.ADMIN_ROLE


# class IsSubEventSuperResponsiblePerson(permissions.BasePermission):
#     message = 'Du darfst dieses Event nicht bearbeiten'

#     def has_permission(self, request: Request, view) -> bool:
#         if not request.user or not request.user.is_authenticated:
#             return False
#         if request.user.is_superuser:
#             return True
#         if request.method == CREATE_METHOD:
#             return True
#         event_id: str = view.kwargs.get('event_pk', None)
#         return check_event_permission(event_id, request, admin_only=True) == EventRole.ADMIN_ROLE


# class IsEventResponsiblePersonOrReadOnly(permissions.BasePermission):
#     message = 'Du darfst dieses Event nicht bearbeiten'

#     def has_permission(self, request: Request, view) -> bool:
#         if not request.user or not request.user.is_authenticated:
#             return False
#         if request.user.is_superuser:
#             return True
#         if request.method in SAFE_METHODS:
#             return True
#         event_id: str = view.kwargs.get("pk", None)
#         return check_event_permission(event_id, request) != EventRole.NONE


# class IsSubEventResponsiblePerson(permissions.BasePermission):
#     message = 'Du darfst dieses Event nicht bearbeiten'

#     def has_permission(self, request: Request, view) -> bool:
#         if not request.user or not request.user.is_authenticated:
#             return False
#         if request.user.is_superuser:
#             return True
#         event_id: str = view.kwargs.get('event_pk', None)
#         return check_event_permission(event_id, request) != EventRole.NONE


# class IsLeaderPerson(permissions.BasePermission):
#     message = 'Du darfst die Statistik dieses Events nicht ansehen'

#     def has_permission(self, request: Request, view) -> bool:
#         if not request.user or not request.user.is_authenticated:
#             return False
#         event_id: str = view.kwargs.get('event_pk', None)
#         return check_leader_permission(event_id, request.user) != EventRole.NONE


# class IsSubEventResponsiblePersonOrReadOnly(permissions.BasePermission):
#     message = 'Du darfst dieses Event nicht bearbeiten'

#     def has_permission(self, request: Request, view) -> bool:
#         if not request.user or not request.user.is_authenticated:
#             return False
#         if request.user.is_superuser:
#             return True
#         if request.method in SAFE_METHODS:
#             return True
#         event_id: str = view.kwargs.get('event_pk', None)
#         return check_event_permission(event_id, request) != EventRole.NONE


# class IsRegistrationResponsiblePerson(permissions.BasePermission):
#     message = 'Du darfst diese Registrierung nicht bearbeiten'

#     def has_permission(self, request: Request, view) -> bool:
#         if not request.user or not request.user.is_authenticated:
#             return False
#         if request.method == CREATE_METHOD:
#             return True
#         if request.user.is_superuser:
#             return True
#         registration_id: str = view.kwargs.get('pk', None)
#         return check_registration_permission(registration_id, request)


# class IsSubRegistrationResponsiblePerson(permissions.BasePermission):
#     message = 'Du darfst diese Registrierung nicht bearbeiten'

#     def has_permission(self, request: Request, view) -> bool:
#         if not request.user or not request.user.is_authenticated:
#             return False
#         if request.user.is_superuser:
#             return True
#         registration_id: str = view.kwargs.get('registration_pk', None)
#         if registration_id is None:
#             registration_id: str = view.kwargs.get('pk', None)
#         return check_registration_permission(registration_id, request)
