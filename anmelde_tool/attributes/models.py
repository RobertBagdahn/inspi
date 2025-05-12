from django.db import models

import anmelde_tool.event.basic.models
from anmelde_tool.attributes.choices import TravelType, AttributeType
from anmelde_tool.registration.models import Registration
from masterdata import models as master_models


class AttributeModule(models.Model):
    """
    if the is_required is set to True the user has explicit do a choice or has to confirm smth.
    min_length, max_length are only relevant for attributes with texts
    tooltip = extra description which appears when hovering above the element
    """

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=1000, null=True)
    text = models.TextField(max_length=10000, null=True)
    is_required = models.BooleanField(default=False)
    min_length = models.IntegerField(default=0)
    max_length = models.IntegerField(default=0)
    tooltip = models.CharField(max_length=1000, null=True, blank=True)
    default_value = models.CharField(max_length=1000, null=True, blank=True)
    field_type = models.CharField(
        max_length=3,
        choices=AttributeType.choices,
        default=AttributeType.IntegerAttribute,
    )
    icon = models.CharField(max_length=25, null=True, blank=True)
    max_entries = models.IntegerField(default=1)
    standard = models.BooleanField(default=False)
    ordering = models.IntegerField(default=1, auto_created=True)
    event_module = models.ForeignKey(
        anmelde_tool.event.basic.models.EventModule,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.title} ({self.event_module.name})"


class AbstractAttribute(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True)
    registration = models.ForeignKey(
        Registration, on_delete=models.CASCADE, null=True, blank=True
    )
    attribute_module = models.ForeignKey(
        AttributeModule, on_delete=models.CASCADE, null=True, blank=True
    )

    class Meta:
        abstract = True


class BooleanAttribute(AbstractAttribute):
    boolean_field = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.attribute_module.title}: {self.boolean_field}"


class DateTimeAttribute(AbstractAttribute):
    date_time_field = models.DateTimeField()

    def __str__(self):
        return f"{self.attribute_module.title}: {self.date_time_field}"


class IntegerAttribute(AbstractAttribute):
    integer_field = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.attribute_module.title}: {self.integer_field}"


class FloatAttribute(AbstractAttribute):
    float_field = models.FloatField()

    def __str__(self):
        return f"{self.attribute_module.title}: {self.float_field}"


class StringAttribute(AbstractAttribute):
    string_field = models.TextField(max_length=10000, blank=True, null=True)

    def __str__(self):
        return f"{self.attribute_module.title}: {self.string_field}"


class DateAttribute(AbstractAttribute):
    date_field = models.DateField()

    def __str__(self):
        return f"{self.attribute_module.title}: {self.date_field}"


class HTMLAttribute(AbstractAttribute):
    html_field = models.TextField(max_length=10000, blank=True, null=True)

    def __str__(self):
        return f"{self.attribute_module.title}: {self.html_field}"


class AttributeChoiceOption(models.Model):
    id = models.AutoField(primary_key=True)
    attribute_module = models.ForeignKey(
        AttributeModule, on_delete=models.CASCADE, related_name="attribute_options"
    )
    text = models.CharField(max_length=1000)
    ordering = models.IntegerField(default=1)

    class Meta:
        ordering = ["ordering"]

    def __str__(self):
        return f"{self.attribute_module.title}: {self.text}"


class RadioAttribute(AbstractAttribute):
    selected_option = models.ForeignKey(
        AttributeChoiceOption,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="selected_option",
    )

    def __str__(self):
        if self.selected_option:
            return f"{self.attribute_module.title}: {self.selected_option.text}"
        return f"{self.attribute_module.title}: None"


class MultiSelectAttribute(AbstractAttribute):
    selected_options = models.ManyToManyField(
        AttributeChoiceOption, blank=True, related_name="selected_options"
    )

    def __str__(self):
        options = ", ".join([option.text for option in self.selected_options.all()])
        return f"{self.attribute_module.title}: {options}"


class ZipCodeAttribute(AbstractAttribute):
    zip_code_field = models.ForeignKey(
        master_models.ZipCode,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.attribute_module.title}: {self.zip_code_field}"


class EmailAttribute(AbstractAttribute):
    email_field = models.EmailField()

    def __str__(self):
        return f"{self.attribute_module.title}: {self.email_field}"


class PhoneAttribute(AbstractAttribute):
    phone_number_field = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.attribute_module.title}: {self.phone_number_field}"


class ScoutGroupAttribute(AbstractAttribute):
    scout_group = models.ForeignKey(
        master_models.ScoutHierarchy,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.attribute_module.title}: {self.scout_group}"
