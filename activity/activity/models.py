import uuid

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    MinLengthValidator,
    MaxLengthValidator,
)
from django.db import models
from pictures.models import PictureField
from colorfield.fields import ColorField
from ckeditor.fields import RichTextField
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from imagekit.models import ProcessedImageField

from activity.activity.choices import OptionType


class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True, editable=False, blank=True, null=True
    )
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    created_by = models.CharField(max_length=20, blank=True, null=True)
    updated_by = models.CharField(max_length=20, blank=True, null=True)
    is_public = models.BooleanField(default=False)

    class Meta:
        abstract = True


class TagCategory(TimeStampMixin):
    id = models.AutoField(auto_created=True, primary_key=True)
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=100, blank=True)
    sorting = models.IntegerField(blank=False, unique=True)
    icon = models.CharField(max_length=20, blank=True, null=True)
    is_header = models.BooleanField(default=False)
    is_mandatory = models.BooleanField(default=False)
    is_activity_overview = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


class MaterialUnit(TimeStampMixin):
    id = models.AutoField(auto_created=True, primary_key=True)
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


class MaterialName(TimeStampMixin):
    id = models.AutoField(auto_created=True, primary_key=True)
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=100, blank=True)
    unit_detaults = models.ForeignKey(MaterialUnit, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


class Tag(TimeStampMixin):
    id = models.AutoField(auto_created=True, primary_key=True)
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=100, blank=True)
    color = ColorField(default="#FF0000")
    icon = models.CharField(max_length=20, blank=True, null=True)
    category = models.ForeignKey(
        TagCategory, on_delete=models.PROTECT, blank=True, null=True
    )
    sorting = models.IntegerField(blank=False, unique=True, null=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


def nameFile(instance, filename):
    return "images/" + str(uuid.uuid1()) + ".jpeg"


class Activity(TimeStampMixin):
    id = models.AutoField(auto_created=True, primary_key=True)
    title = models.CharField(
        max_length=45, validators=[MinLengthValidator(5), MaxLengthValidator(40)]
    )
    description = RichTextField(
        max_length=8000, default="", validators=[MaxLengthValidator(8000)]
    )
    summary = models.CharField(
        max_length=100, default="", validators=[MaxLengthValidator(100)]
    )
    tags = models.ManyToManyField(Tag, default="")
    costs_rating = models.SmallIntegerField(
        default=1, validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    execution_time = models.SmallIntegerField(
        default=1, validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    preparation_time = models.SmallIntegerField(
        default=1, validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    difficulty = models.SmallIntegerField(
        default=1, validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    created_by_email = models.CharField(max_length=60, blank=True)
    like_score = models.IntegerField(default=0)
    view_count = models.IntegerField(default=0)
    front_image = PictureField(
        upload_to="static/front_images",
        blank=True,
        null=True,
        width_field=200,
        height_field=200,
    )

    def _get_stufen_string(self):
        tags = self.tags.all()
        tags = tags.filter(category_id=3)
        return " und ".join([tag.name for tag in tags])

    def _get_art_string(self):
        tags = self.tags.all()
        tags = tags.filter(category_id=4)
        return " und ".join([tag.name for tag in tags])

    stufen_string = property(_get_stufen_string)
    art_string = property(_get_art_string)

    def __str__(self):
        return self.title

    def __repr__(self):
        return self.__str__()


class MaterialItem(TimeStampMixin):
    id = models.AutoField(auto_created=True, primary_key=True)
    quantity = models.IntegerField(default=0)
    number_of_participants = models.IntegerField(default=0, blank=True)
    material_name = models.ForeignKey(MaterialName, on_delete=models.PROTECT)
    material_unit = models.ForeignKey(MaterialUnit, on_delete=models.PROTECT)
    activity = models.ForeignKey(
        Activity,
        related_name="material_list",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.material_name

    def __repr__(self):
        return self.__str__()


class Like(TimeStampMixin):
    id = models.AutoField(auto_created=True, primary_key=True)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    opinion_type_id = models.IntegerField(
        choices=OptionType.choices, default=OptionType.LIKE
    )
    like_created = models.DateTimeField(auto_now_add=True, editable=False)


class Experiment(TimeStampMixin):
    id = models.AutoField(auto_created=True, primary_key=True)
    age_level = models.IntegerField(blank=False, unique=False, null=True)
    group_type = models.IntegerField(blank=False, unique=False, null=True)
    group_leader = models.IntegerField(blank=False, unique=False, null=True)

    def __str__(self):
        return f"{self.id} {self.age_level} {self.group_type} {self.group_leader}"

    def __repr__(self):
        return self.__str__()


class ExperimentItem(TimeStampMixin):
    id = models.AutoField(auto_created=True, primary_key=True)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    score = models.IntegerField(blank=False, unique=False, null=True)

    def __str__(self):
        return f"{self.activity} {self.experiment} {self.score}"

    def __repr__(self):
        return self.__str__()


class NextBestHeimabend(TimeStampMixin):
    id = models.AutoField(auto_created=True, primary_key=True)
    activity = models.ForeignKey(Activity, related_name="ref", on_delete=models.CASCADE)
    activity_score = models.ForeignKey(
        Activity, related_name="score", on_delete=models.CASCADE
    )
    score = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True)

    def __str__(self):
        return "{} - {}".format(self.activity, self.activity_score)

    def __repr__(self):
        return self.__str__()


class ActivityOfTheWeek(TimeStampMixin):
    id = models.AutoField(auto_created=True, primary_key=True)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    release_date = models.DateField(blank=True, null=True)
    tags = models.ManyToManyField(Tag, default="")
    comment = models.CharField(max_length=2000, blank=True, null=True)

    def save(self, *args, **kwargs):
        if (
            ActivityOfTheWeek.objects.exclude(pk=self.pk)
            .filter(release_date=self.release_date)
            .exists()
        ):
            raise ValidationError(
                "An dem Montag existier bereits ein Heimabend der Woche."
            )
        if (
            ActivityOfTheWeek.objects.exclude(pk=self.pk)
            .filter(activity_id=self.activity_id)
            .exists()
        ):
            raise ValidationError("Dieser Heimabend wurde bereits ausgewählt.")

        super(ActivityOfTheWeek, self).save(*args, **kwargs)

    def __str__(self):
        return "{} - {}".format(self.activity, self.release_date)

    def __repr__(self):
        return self.__str__()


class Profile(models.Model):
    avatar_thumbnail = ProcessedImageField(
        upload_to="avatars",
        processors=[ResizeToFill(100, 50)],
        format="JPEG",
        options={"quality": 60},
    )
