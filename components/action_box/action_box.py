from django_components import component


@component.register("action-box")
class ActionButtonComponent(component.Component):
    template_name = "action_box/action_box.html"

    def get_context_data(self, text="Suchen", color="blue", icon="search", link="", description=""):
        return {
            "text": text,
            "color": color,
            "icon": icon,
            "link": link,
            "description": description
        }
