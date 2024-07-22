from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'add users'

    def handle(self, *args, **options):
        UserModel = get_user_model()

        if not UserModel.objects.filter(username='admin').exists():
            user = UserModel.objects.create_user('admin', password='admin', email="admin@admin.de", scout_display_name="admin")

            user.is_superuser = True
            user.is_staff = True
            user.save()

        if not UserModel.objects.filter(username='staff').exists():
            user = UserModel.objects.create_user('staff', password='staff', email="staff@staff.de", scout_display_name="staff")

            user.is_superuser = False
            user.is_staff = True
            user.save()
    
        if not UserModel.objects.filter(username='user').exists():
            user = UserModel.objects.create_user('user', password='user', email="user@user.de", scout_display_name="user")

            user.is_superuser = False
            user.is_staff = False
            user.save()
    
        if not UserModel.objects.filter(username='author1').exists():
            user = UserModel.objects.create_user('author1', password='author1', email="author1@author1.de", scout_display_name="author1")

            user.is_superuser = False
            user.is_staff = False
            user.save()

        print('user created')
