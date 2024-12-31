from django_components import component


@component.register("kpi-box")
class KpiBoxComponent(component.Component):
    template_name = "kpi_box/kpi_box.html"

    def get_context_data(self, kpi_value="1", color="blue", kpi_description="", link="", link_text="", icon=""):
        return {
            "kpi_value": kpi_value,
            "color": color,
            "kpi_description": kpi_description,
            "link": link,
            "link_text": link_text,
            "icon": icon
        }
