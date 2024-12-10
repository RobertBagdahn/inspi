import uuid
from random import randint

from django.contrib.auth import get_user_model

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

from image_cropping import ImageRatioField, ImageCropField


from .choices import (
    ExecutionTimeChoices,
    DifficultyChoices,
    CostsRatingChoices,
    PrepairationTimeChoices,
    StatusChoices,
    StatusChoicesAdmin,
    EmotionType,
)

from general.login.models import CustomUser
User = get_user_model()


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


class Topic(TimeStampMixin):
    id = models.AutoField(auto_created=True, primary_key=True)
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=100, blank=True)
    sorting = models.IntegerField(blank=False, unique=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.description}"

    def __repr__(self):
        return self.__str__()


class ActivityTypeChoice(TimeStampMixin):
    id = models.AutoField(auto_created=True, primary_key=True)
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=100, blank=True)
    sorting = models.IntegerField(blank=False, unique=True, null=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


class TimeChoice(TimeStampMixin):
    id = models.AutoField(auto_created=True, primary_key=True)
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=100, blank=True)
    sorting = models.IntegerField(blank=False, unique=True, null=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


class LocationChoice(TimeStampMixin):
    id = models.AutoField(auto_created=True, primary_key=True)
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=100, blank=True)
    sorting = models.IntegerField(blank=False, unique=True, null=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


class ScoutLevelChoice(TimeStampMixin):
    id = models.AutoField(auto_created=True, primary_key=True)
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=100, blank=True)
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
        max_length=45,
        default="",
        validators=[MinLengthValidator(5), MaxLengthValidator(45)],
    )
    summary = models.CharField(
        max_length=300, default="", validators=[MaxLengthValidator(300)]
    )
    summary_long = models.CharField(
        max_length=1000,
        default="",
        validators=[MaxLengthValidator(1000)],
        blank=True,
    )
    description = RichTextField(
        max_length=8000, default="", validators=[MaxLengthValidator(8000)]
    )

    costs_rating = models.CharField(
        choices=CostsRatingChoices.choices,
        default=CostsRatingChoices.ZERO,
        max_length=20,
    )
    execution_time = models.CharField(
        choices=ExecutionTimeChoices.choices,
        default=ExecutionTimeChoices.LESS_THAN_30,
        max_length=20,
    )
    preparation_time = models.CharField(
        choices=PrepairationTimeChoices.choices,
        default=PrepairationTimeChoices.LESS_THAN_30,
        max_length=20,
    )
    difficulty = models.CharField(
        choices=DifficultyChoices.choices,
        default=DifficultyChoices.EASY,
        max_length=20,
    )

    scout_levels = models.ManyToManyField(ScoutLevelChoice, default="")
    activity_types = models.ManyToManyField(ActivityTypeChoice, default="")
    locations = models.ManyToManyField(LocationChoice, default="")
    times = models.ManyToManyField(TimeChoice, default="")

    topics = models.ManyToManyField(Topic, default="")

    created_by_name = models.CharField(max_length=60, blank=True)
    created_by_email = models.CharField(max_length=60, blank=True)
    authors = models.ManyToManyField(CustomUser, blank=True)
    status = models.CharField(
        choices=StatusChoicesAdmin.choices,
        default=StatusChoicesAdmin.DRAFT,
        max_length=20,
    )

    like_score = models.IntegerField(default=0)
    view_count = models.IntegerField(default=0)
    image = models.ImageField(blank=True, upload_to="static/activity/uploaded_images")
    cropping = ImageRatioField("image", "400x400")

    def _get_stufen_string(self):
        _str = ""
        if len(self.scout_levels.all()) == 3:
            return "Für alle"

        for stufe in self.scout_levels.all():
            if stufe == self.scout_levels.all().last():
                _str += stufe.name
            else:
                _str += stufe.name + " + "
        return _str

    def _get_art_string(self):
        _str = ""
        for art in self.activity_types.all():
            # when count 3 then 'all'

            if art == self.activity_types.all().last():
                _str += art.name
            else:
                _str += art.name + " + "

        return _str

    def _get_location_string(self):

        _str = ""
        if len(self.locations.all()) == 3:
            return "Überall"

        for location in self.locations.all():
            if location == self.locations.all().last():
                _str += location.name
            else:
                _str += location.name + ", "

        return _str

    def _get_time_string(self):
        _str = ""
        if len(self.times.all()) == 3:
            return "Immer"

        for time in self.times.all():
            if time == self.times.all().last():
                _str += time.name
            else:
                _str += time.name + ", "
        return _str

    scout_levels_string = property(_get_stufen_string)
    activity_types_string = property(_get_art_string)
    location_string = property(_get_location_string)
    time_string = property(_get_time_string)

    def is_allowed_to_edit(self, user):
        # user in authors
        return user.is_staff or user.is_superuser

    # An alternative to use to update the view count
    def update_views(self, *args, **kwargs):
        self.view_count = self.view_count + 1
        super(Activity, self).save(*args, **kwargs)

    # add get_absolute_url
    def get_absolute_url(self):
        return f"/activity/details/{self.id}"

    def __str__(self):
        return f"{self.title} - {self.created_by_email}"

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
        return f"{self.quantity} x {self.material_name.name} {self.material_unit.name}"

    def __repr__(self):
        return self.__str__()


class Emotion(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    emotion = models.CharField(
        choices=EmotionType.choices, default=EmotionType.HAPPY, max_length=20
    )
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    created_by = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="emotion_activity", null=True, blank=True
    )

    def __str__(self):
        return f"{self.activity.title} {self.emotion}" + " - " + str(self.created_by)
    
    def __repr__(self):
        return self.__str__()


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

        super(ActivityOfTheWeek, self).save(*args, **kwargs)

    def __str__(self):
        return "{} {}".format(self.activity, self.release_date)

    def __repr__(self):
        return self.__str__()


class Profile(models.Model):
    avatar_thumbnail = ProcessedImageField(
        upload_to="avatars",
        processors=[ResizeToFill(100, 50)],
        format="JPEG",
        options={"quality": 60},
    )


class Comment(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="author_actvity"
    )
    content = RichTextField(max_length=8000, default="")
    date_posted = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="replies_actvity",
    )
    is_approved = models.BooleanField(default=False)

    class Meta:
        ordering = ["-date_posted"]

    def __str__(self):
        return str(self.author) + ": " + str(self.content) + " - " + str(self.activity) + " - " + str(self.is_approved)

    @property
    def children(self):
        return Comment.objects.filter(parent=self).reverse()

    @property
    def is_parent(self):
        if self.parent is None:
            return True
        return False

    def is_allowed_to_edit(self, user):
        # user in authors
        return user.is_staff or user.is_superuser
