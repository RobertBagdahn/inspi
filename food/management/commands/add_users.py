from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'add users'

    def handle(self, *args, **options):
        UserModel = get_user_model()

        if not UserModel.objects.filter(username='admin').exists():
            user_1 = UserModel.objects.create_user('admin', password='admin1234')
            user_1.is_superuser = True
            user_1.is_staff = True
            user_1.save()

        print('user created')
