from django_components import component


@component.register("link-button")
class LinkButtonComponent(component.Component):
    template_name = "link_button/link_button.html"

    def get_context_data(
        self,
        color="blue",
        text="",
        icon="",
        url="",
    ):
        return {
            "color": color,
            "text": text,
            "icon": icon,
            "url": url,
        }

    class Media:
        css = "link_button/link_button.css"
        js = "link_button/link_button.js"
