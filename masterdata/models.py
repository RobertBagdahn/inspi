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
            self.status = "upcoming"
        elif self.exist_from <= now and (self.exist_till is None or self.exist_till >= now):
            self.status = "active"
        elif self.exist_till and self.exist_till < now:
            self.status = "inactive"
        else:
            self.status = "unknown"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.level_choice} - {self.name} - {self.bund}"


class EatHabit(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True)
    name = models.CharField(max_length=100)
    public = models.BooleanField(default=False)

    def __str__(self):
        return self.name