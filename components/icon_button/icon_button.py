from django_components import component


@component.register("icon-button")
class IconButtonComponent(component.Component):
    template_name = "icon_button/icon_button.html"

    def get_context_data(
        self,
        color="blue",
        icon="",
        url="",
    ):
        return {
            "color": color,
            "icon": icon,
            "url": url,
        }
