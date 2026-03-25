from django.contrib import admin
from .models import Category, Post, Comment

admin.site.register(Category)
admin.site.register(Post)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'post', 'date_posted', 'is_published']
    list_filter = ['is_published', 'date_posted']
    list_editable = ['is_published']
    actions = ['publish_comments', 'unpublish_comments']

    @admin.action(description='Kommentare veröffentlichen')
    def publish_comments(self, request, queryset):
        queryset.update(is_published=True)

    @admin.action(description='Kommentare zurückziehen')
    def unpublish_comments(self, request, queryset):
        queryset.update(is_published=False)