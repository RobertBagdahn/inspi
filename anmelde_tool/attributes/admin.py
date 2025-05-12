from django.contrib import admin

from .models import (
    BooleanAttribute,
    DateTimeAttribute,
    IntegerAttribute,
    FloatAttribute,
    StringAttribute,
    AttributeModule,
    DateAttribute,
    HTMLAttribute,
    AttributeChoiceOption,
    RadioAttribute,
    MultiSelectAttribute,
    ZipCodeAttribute,
    EmailAttribute,
    PhoneAttribute,
    ScoutGroupAttribute,
)


class BaseAdmin(admin.ModelAdmin):
    list_display = ("id", "registration", "attribute_module")
    search_fields = (
        "registration",
        "attribute_module__title",
        "attribute_module__text",
    )
    list_filter = ("registration", "attribute_module")


@admin.register(BooleanAttribute)
class BooleanAttributeAdmin(BaseAdmin):
    list_display = ("id", "registration", "attribute_module", "boolean_field")


@admin.register(DateTimeAttribute)
class DateTimeAttributeAdmin(BaseAdmin):
    list_display = ("id", "registration", "attribute_module", "date_time_field")


@admin.register(IntegerAttribute)
class IntegerAttributeAdmin(BaseAdmin):
    list_display = ("id", "registration", "attribute_module", "integer_field")


@admin.register(FloatAttribute)
class FloatAttributeAdmin(BaseAdmin):
    list_display = ("id", "registration", "attribute_module", "float_field")


@admin.register(StringAttribute)
class StringAttributeAdmin(BaseAdmin):
    list_display = ("id", "registration", "attribute_module", "string_field")


@admin.register(DateAttribute)
class DateAttributeAdmin(BaseAdmin):
    list_display = ("id", "registration", "attribute_module", "date_field")


@admin.register(HTMLAttribute)
class HTMLAttributeAdmin(BaseAdmin):
    list_display = ("id", "registration", "attribute_module")


@admin.register(AttributeChoiceOption)
class RadioChoiceOptionAdmin(admin.ModelAdmin):
    list_display = ("id", "attribute_module", "text", "ordering")
    search_fields = ("attribute_module__title", "text")
    list_filter = ("attribute_module",)


@admin.register(RadioAttribute)
class RadioAttributeAdmin(BaseAdmin):
    list_display = ("id", "registration", "attribute_module", "selected_option")


@admin.register(MultiSelectAttribute)
class MultiSelectAttributeAdmin(BaseAdmin):
    list_display = ("id", "registration", "attribute_module")


@admin.register(ZipCodeAttribute)
class ZipCodeAttributeAdmin(BaseAdmin):
    list_display = ("id", "registration", "attribute_module", "zip_code_field")


@admin.register(EmailAttribute)
class EmailAttributeAdmin(BaseAdmin):
    list_display = ("id", "registration", "attribute_module", "email_field")


@admin.register(PhoneAttribute)
class PhoneAttributeAdmin(BaseAdmin):
    list_display = ("id", "registration", "attribute_module", "phone_number_field")


@admin.register(ScoutGroupAttribute)
class ScoutGroupAttributeAdmin(BaseAdmin):
    list_display = ("id", "registration", "attribute_module", "scout_group")


@admin.register(AttributeModule)
class AttributeEventModuleMapperAdmin(admin.ModelAdmin):
    list_display = ("id", "text", "standard", "event_module", "field_type")
    search_fields = ("event_module",)
    list_filter = ("event_module",)
