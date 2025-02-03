from django.contrib import admin
from .models import InspiGroup, InspiGroupMembership, InspiGroupJoinRequest, InspiGroupPermission, InspiGroupNews

admin.site.register(InspiGroup)
admin.site.register(InspiGroupMembership)
admin.site.register(InspiGroupJoinRequest)
admin.site.register(InspiGroupPermission)
admin.site.register(InspiGroupNews)