from django.db import models
from masterdata.choices import ScoutOrganisationLevelChoices, StateChoices
from django.utils.text import slugify
from django.utils import timezone



class ZipCode(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True)
    zip_code = models.CharField(max_length=5, blank=True)
    city = models.CharField(max_length=60, blank=True)
    lat = models.DecimalField(max_digits=20, decimal_places=15, default=0.000)
    lon = models.DecimalField(max_digits=20, decimal_places=15, default=0.000)
    state = models.CharField(max_length=2, choices=StateChoices.choices, default=StateChoices.BY)
    created_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return f"{self.zip_code} {self.city}"

    

class ScoutHierarchy(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True)
    name = models.CharField(max_length=60, blank=True)
    slug = models.SlugField(max_length=60, unique=True, null=True, blank=True)
    abbreviation = models.CharField(max_length=5, blank=True, null=True)
    full_name = models.CharField(max_length=200, blank=True, null=True)
    description = models.CharField(max_length=1000, blank=True)
    level_choice = models.CharField(
        max_length=10,
        choices=ScoutOrganisationLevelChoices.choices,
        default=ScoutOrganisationLevelChoices.GRUPPE
    )
    zip_code = models.ForeignKey(ZipCode, on_delete=models.PROTECT, null=True, blank=True)
    parent = models.ForeignKey('self', null=True, on_delete=models.PROTECT, related_name='scouthierarchy', blank=True)
    created_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    exist_from = models.DateField(blank=True, null=True, default="1970-01-01")
    exist_till = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=60, blank=True, null=True)

    @property
    def children(self):
        return ScoutHierarchy.objects.filter(parent=self.id)
    
    @property
    def all_childen_count(self):
        def count_children(hierarchy):
            count = 0
            for child in hierarchy.children:
                if child.level_choice == 'Stamm':
                    count += 1
                count += count_children(child)
            return count

        return count_children(self)


    @property
    def bund(self):
        iterator: ScoutHierarchy = self
        while iterator is not None:
            if iterator.level_choice == 'Bund':
                return iterator.name
            iterator = iterator.parent

    @property
    def verband(self):
        iterator: ScoutHierarchy = self
        while iterator is not None:
            if iterator.level_choice == 'Verband':
                return iterator.name
            iterator = iterator.parent

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        
        now = timezone.now().date()
        if self.exist_from > now and self.exist_till is None:
            print("upcoming")
            self.status = "upcoming"
        elif self.exist_from <= now and (self.exist_till is None or self.exist_till >= now):
            print("active")
            self.status = "active"
        elif self.exist_till and self.exist_till < now:
            print("inactive")
            self.status = "inactive"
        else:
            print("unknown")
            self.status = "unknown"
        print("fdsgd")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.level_choice} - {self.name} - {self.bund}"


class NutritionalTag(models.Model):
    name = models.CharField(
        max_length=255,
        help_text="Name of the tag. E.g. 'Fleisch', 'Alkohol', 'Nüsse', Scharf",
    )
    name_opposite = models.CharField(
        max_length=255,
        help_text="Name of the tag for human readable output. e.g. 'Vegan', 'Vegetarisch', 'Alkoholfrei'",
    )
    description = models.CharField(max_length=255)
    description_human = models.CharField(max_length=255)
    rank = models.IntegerField(default=1)
    is_dangerous = models.BooleanField(
        default=False,
        help_text="Indicates if this tag represents a potentially harmful or dangerous ingredient",
    )
    default_in_event = models.BooleanField(
        default=False,
        help_text="Indicates if this tag is automatically included in the event",
    )
    created_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()
    

class EventLocation(models.Model):
    name = models.CharField(max_length=60)
    description = models.CharField(max_length=200, blank=True)
    zip_code = models.ForeignKey(
        ZipCode, on_delete=models.PROTECT, null=True, blank=True
    )
    address = models.CharField(max_length=60, blank=True)
    contact_name = models.CharField(max_length=30, blank=True)
    contact_email = models.CharField(max_length=30, blank=True)
    contact_phone = models.CharField(max_length=30, blank=True)
    per_person_fee = models.FloatField(blank=True, null=True)
    fix_fee = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return f"{self.name}: ({self.address}, {self.zip_code})"

    class Meta:
        verbose_name = "Veranstaltungsort"
        verbose_name_plural = "Veranstaltungsorte"
        ordering = ["name"]


class EatHabit(models.Model):
    name = models.CharField(max_length=60, blank=True)
    description = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Ernährungsgewohnheit"
        verbose_name_plural = "Ernährungsgewohnheiten"
        ordering = ["name"]