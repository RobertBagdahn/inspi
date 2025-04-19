from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Person, CustomUser

@receiver(post_save, sender=Person)
def update_auth_level(sender, instance, created, **kwargs):
    """
    Update the auth level of the user when a person is created or updated.
    """

    person = instance
    # get the user associated with the person
    user = CustomUser.objects.filter(person=instance).first()
    # check if the user is not None
    if user:
        print(f"Updating auth level for user: {user.username}")
        # update the auth level based on the person instance
        if user.is_superuser or user.is_staff:
            user.auth_level = 5
        elif person.is_staff:
            user.auth_level = 3
        else:
            user.auth_level = 1

        # save the user instance
        user.save()
    else:
        # if the user is None, log an error or handle it as needed
        print(f"User not found for person: {person}")


