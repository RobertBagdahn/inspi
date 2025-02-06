from django_components import component


@component.register("icon")
class IconComponent(component.Component):
    template_name = "icon/icon.html"

    def get_context_data(self, icon="Suchen", color="blue", size="md", align=""):
        return {
            "icon": icon,
            "color": color,
            "size": size,
            "align": align
        }
