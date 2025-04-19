from django.contrib import admin

from .models import BooleanAttribute, DateTimeAttribute, IntegerAttribute, FloatAttribute, \
    TravelAttribute, StringAttribute, AttributeModule


class BaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'registration', 'attribute_module')
    search_fields = ('registration', 'attribute_module__title', 'attribute_module__text')
    list_filter = ('registration', 'attribute_module')


@admin.register(BooleanAttribute)
class BooleanAttributeAdmin(BaseAdmin):
    list_display = ('id', 'registration', 'attribute_module', 'boolean_field')


@admin.register(DateTimeAttribute)
class DateTimeAttributeAdmin(BaseAdmin):
    pass


@admin.register(IntegerAttribute)
class IntegerAttributeAdmin(BaseAdmin):
    pass


@admin.register(FloatAttribute)
class FloatAttributeAdmin(BaseAdmin):
    pass


@admin.register(TravelAttribute)
class TravelAttributeAdmin(BaseAdmin):
    pass


@admin.register(StringAttribute)
class StringAttributeAdmin(BaseAdmin):
    pass


@admin.register(AttributeModule)
class AttributeEventModuleMapperAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'standard', 'event_module', 'field_type')
    search_fields = ('event_module',)
    list_filter = ('event_module',)
