from django_components import component


@component.register("submit-button")
class SubitButtonComponent(component.Component):
    template_name = "submit_button/submit_button.html"

    def get_context_data(self, text="Suchen", color="blue", icon="search"):
        return {
            "text": text,
            "color": color,
            "icon": icon,
        }
