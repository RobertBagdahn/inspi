from allauth.socialaccount.models import SocialAccount

from group.models import InspiGroup, InspiGroupMembership
from general.login.models import Person  # Assuming Person is defined in this path


def update_person_user_from_keycloak(instance):
    """
    Update the person_user field of the CustomUser instance before saving.
    """

    print(f"Updating person_user for user: {instance.username}")

    # Try to get the social account connected to this user
    try:
        social_account = SocialAccount.objects.get(user=instance)
        print(
            f"Found social account: {social_account.provider} for user {instance.username}"
        )

        # Get or create a new Person object for this user
        extra_data = social_account.extra_data
        person = Person.objects.filter(user=instance).first()

        if not person:
            person = Person(user=instance)

        # Map fields from social account extra_data to person object
        for key, value in extra_data.items():
            # Skip roles array
            if key == "roles":
                continue

            # Check if person model has this attribute
            if hasattr(person, key):
                setattr(person, key, value)

            # Special mappings
            if key == "fahrtenname":
                person.scout_name = value
                instance.scout_display_name = value
            elif key == "given_name":
                person.first_name = value
                instance.first_name = value
            elif key == "family_name":
                person.last_name = value
                instance.last_name = value
            elif key == "email":
                person.email = value

        instance.is_dpv_idm = True

        # Save the user instance
        instance.save()

        # Link the person to the user - update the forward relation
        person.user = instance
        person.save()

        # No need to save instance again as we're not modifying it directly

    except SocialAccount.DoesNotExist:
        print(f"No social account found for user: {instance.username}")
    except SocialAccount.MultipleObjectsReturned:
        # Handle case where there are multiple social accounts
        print(f"Multiple social accounts found for user: {instance.username}")


def update_groups_from_keycloak(instance):
    """
    Update the groups of the user based on the Keycloak roles.
    """
    print(f"Updating groups for user: {instance.username}")

    try:
        social_account = SocialAccount.objects.get(user=instance)
        extra_data = social_account.extra_data

        # Check if roles exist in extra_data
        if "roles" in extra_data:

            # Get all the roles
            roles = extra_data.get("roles", [])

            # Filter out roles starting with "group_"
            valid_roles = [
                role
                for role in roles
                if not (role.startswith('group-') or role.startswith('query') or role.startswith('view'))
            ]

            for role in valid_roles:
                # Try to find existing Inspi_Group or create a new one
                try:
                    inspi_group = InspiGroup.objects.get(
                        name=role,
                    )
                except InspiGroup.DoesNotExist:
                    # If the group does not exist, create it
                    inspi_group = InspiGroup.objects.create(
                        name=role,
                        description=f"Keycloak Gruppe: {role}",
                        is_visible=True,
                        created_by=instance,
                        free_to_join=False,
                        is_keycloak_group=True,
                    )
                    print(f"Created new group: {inspi_group.name}")

                # Check if membership already exists
                try:
                    membership = InspiGroupMembership.objects.get(
                        user=instance,
                        group=inspi_group,
                    )
                    created = False
                except InspiGroupMembership.DoesNotExist:
                    # Create a new membership if it doesn't exist
                    membership = InspiGroupMembership.objects.create(
                        user=instance,
                        group=inspi_group,
                        created_by=instance,
                    )
                    created = True

                if created:
                    print(
                        f"Created new membership in group '{inspi_group.name}' for user {instance.username}"
                    )
                else:
                    print(
                        f"User {instance.username} already has membership in group '{inspi_group.name}'"
                    )

            # Save the user to ensure group memberships are saved
            instance.save()

    except SocialAccount.DoesNotExist:
        print(f"No social account found for user: {instance.username}")
    except Exception as e:
        print(f"Error updating groups for user {instance.username}: {str(e)}")
