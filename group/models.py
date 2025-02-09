# models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.utils import timezone

from ckeditor.fields import RichTextField


User = get_user_model()


class InspiGroup(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="created_groups"
    )
    is_visible = models.BooleanField(default=True)
    free_to_join = models.BooleanField(default=True)
    join_code = models.CharField(max_length=20, blank=True, null=True, unique=True)
    editable_by_users = models.ManyToManyField(User, related_name="editable_groups")
    editable_by_groups = models.ManyToManyField(
        "self", symmetrical=False, related_name="editable_subgroups", blank=True, null=True
    )
    is_deleted = models.BooleanField(default=False)
    date_deleted = models.DateTimeField(blank=True, null=True)
    delete_requested_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="group_cancellation_requests", blank=True, null=True
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        
        super().save(*args, **kwargs)

        if self.created_by not in self.editable_by_users.all():
            self.editable_by_users.add(self.created_by)

    def __str__(self):
        return self.name
    
    @property
    def memberships(self):
        return self.inspigroupmembership_set.all()
    
    @property
    def admins(self):
        return self.editable_by_users.all()
    
    @property
    def join_requests(self):
        return self.inspigroupjoinrequest_set.all()
    
    @property
    def permissions(self):
        return self.permissions.all()
    
    @property
    def parent_admin_groups(self):
        return self.editable_by_groups.all()
    
    @property
    def parent_groups(self):
        return InspiGroup.objects.filter(subgroup_permissions__group=self)
    
    @property
    def subgroups(self):
        return self.editable_subgroups.all()
    
    @property
    def is_not_deleted(self):
        return not self.is_deleted
    


class InspiGroupMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(InspiGroup, on_delete=models.CASCADE)
    date_joined = models.DateTimeField(auto_now_add=True)
    read_access = models.BooleanField(default=False)
    full_access = models.BooleanField(default=False)
    share_all_personal_data = models.BooleanField(default=True)
    share_own_personal_data = models.BooleanField(default=True)
    is_cancelled = models.BooleanField(default=False)
    date_cancelled = models.DateTimeField(blank=True, null=True)
    cancel_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="cancellation_requests", blank=True, null=True
    )

    def __str__(self):
        return f"{self.user.username} in {self.group.name}"
    
    @property
    def status(self):
        if self.is_cancelled:
            return "member_cancelled"
        
        if self.full_access:
            return "member_full_access"
        
        if self.read_access:
            return "member_read_access"
        
        return "Member_no_access"
    
    @property
    def is_not_cancelled(self):
        return not self.is_cancelled
    


    
class InspiGroupJoinRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(InspiGroup, on_delete=models.CASCADE)
    date_requested = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=None, blank=True, null=True)
    date_checked = models.DateTimeField(blank=True, null=True)
    user_checked_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="checked_requests", blank=True, null=True
    )

    def __str__(self):
        return f"'{self.user.username}' fragt für '{self.group.name}'"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.approved:
            InspiGroupMembership.objects.get_or_create(user=self.user, group=self.group)


class InspiGroupPermission(models.Model):
    parent_group = models.ForeignKey(
        InspiGroup, on_delete=models.CASCADE, related_name="subgroup_permissions", blank=True, null=True
    )
    group = models.ForeignKey(
        InspiGroup, on_delete=models.CASCADE, related_name="permissions"
    )
    read_access = models.BooleanField(default=False)
    full_access = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="created_permissions", blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"{self.group.name} gave permissions to {self.parent_group.name}"
    
class InspiGroupNews(models.Model):
    id = models.AutoField(primary_key=True)
    group = models.ForeignKey(InspiGroup, on_delete=models.CASCADE, related_name="news")
    subject = models.CharField(max_length=255)
    message = RichTextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_group_news")
    is_visible = models.BooleanField(default=True)