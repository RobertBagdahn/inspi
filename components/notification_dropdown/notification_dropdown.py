from django_components import component
from general.notification.models import NotificationMessage


@component.register("notification-dropdown")
class NotificationDropdownComponent(component.Component):
    template_name = "notification_dropdown/notification_dropdown.html"

    def get_context_data(self, user):
        notifications = NotificationMessage.objects.filter(is_read=False).filter(user = user)
        print(f"Nachrichten: {notifications}")

        return {
            "notifications": notifications
        }
