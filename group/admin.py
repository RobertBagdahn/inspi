from django.contrib import admin
from .models import InspiGroup, InspiGroupMembership, InspiGroupJoinRequest, InspiGroupPermission

admin.site.register(InspiGroup)
admin.site.register(InspiGroupMembership)
admin.site.register(InspiGroupJoinRequest)
admin.site.register(InspiGroupPermission)
