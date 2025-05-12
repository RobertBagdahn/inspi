import logging
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Person, CustomUser
from allauth.socialaccount.models import SocialAccount
from django.contrib import messages
from allauth.socialaccount.signals import pre_social_login
from .service import update_person_user_from_keycloak, update_groups_from_keycloak


@receiver(post_save, sender=Person)
def update_auth_level(sender, instance, created, **kwargs):
    """
    Update the auth level of the user when a person is created or updated.
    """

    person = instance
    # get the user associated with the person
    user = CustomUser.objects.filter(person_user=instance).first()
    # check if the user is not None
    if user:
        print(f"Updating auth level for user: {user.username}")
        # update the auth level based on the person instance
        if user.is_superuser or user.is_staff:
            user.auth_level = 5
        else:
            user.auth_level = 1

        # save the user instance
        user.save()
    else:
        # if the user is None, log an error or handle it as needed
        print(f"User not found for person: {person}")


@receiver(pre_social_login)
def link_social_account_to_person(sender, request, sociallogin, **kwargs):
    """
    Link a social account to a person when a user logs in via social auth.
    This runs before the user is logged in.
    """
    user = sociallogin.user

    logging.info(f"Linking social account to person for user: {user.username}")

    if not user.id:  # New user, not saved yet
        # We'll handle this in the post_save signal once the user is created
        logging.info("New user detected, skipping person update.")
        return

    # For existing users, update their person information from social data
    if hasattr(sociallogin, "account"):
        instance = user
        logging.info(f"Updating person_user for user: {instance.username}")

        logging.info(
            f"Found social account: {sociallogin.account.provider} for user {instance.username}"
        )

        # Get or update the person linked to this user
        update_person_user_from_keycloak(instance)
        update_groups_from_keycloak(instance)
