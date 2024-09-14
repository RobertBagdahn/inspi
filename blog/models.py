from django.contrib.auth import get_user_model
from django.db import models
from ckeditor.fields import RichTextField

User = get_user_model()

from .choices import StatusType


class Category(models.Model):
    title = models.CharField(max_length=20)
    subtitle = models.CharField(max_length=100)
    slug = models.SlugField()
    thumbnail = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.title


class Post(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField()
    overview = models.TextField(max_length=200)
    timestamp_created = models.DateTimeField(auto_now_add=True)
    timestamp_published = models.DateTimeField(
        auto_now_add=False, auto_now=False, null=True, blank=True
    )
    content = RichTextField(max_length=8000, default="")
    words = models.IntegerField(default=0)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    thumbnail = models.ImageField(null=True, blank=True)
    categories = models.ManyToManyField(Category)
    status = models.CharField(
        max_length=10, choices=StatusType.choices, default=StatusType.DRAFT
    )

    # add get_absolute_url
    def get_absolute_url(self):
        return f"/blog/post/{self.slug}"

    def __str__(self):
        return f"{self.title} by {self.author}"

    def is_allowed_to_edit(self, user):
        return user == self.author or user.is_staff or user.is_superuser

    def save(self, *args, **kwargs):
        self.words = len(self.content.split())
        super().save(*args, **kwargs)

    def as_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "overview": self.overview,
            "content": self.content,
            "slug": self.slug,
        }


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = RichTextField(max_length=8000, default="")
    date_posted = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies"
    )

    class Meta:
        ordering = ["-date_posted"]

    def __str__(self):
        return str(self.author) + " comment " + str(self.content)

    @property
    def children(self):
        return Comment.objects.filter(parent=self).reverse()

    @property
    def is_parent(self):
        if self.parent is None:
            return True
        return False
