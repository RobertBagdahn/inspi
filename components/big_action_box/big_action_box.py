from django_components import component


@component.register("big-action-box")
class BigActionBoxComponent(component.Component):
    template_name = "big_action_box/big_action_box.html"

    def get_context_data(
        self,
        header="Gruppe mit Code beitreten",
        icon="",
        color="blue",
        description="Geben Sie den von Ihrem Gruppenleiter bereitgestellten Code ein, um der Gruppe beizutreten.",
        button_text="Beitreten mit Code",
        url=None,
        post_url=None,
    ):
        return {
            "header": header,
            "icon": icon,
            "color": color,
            "description": description,
            "button_text": button_text,
            "url": url,
            "post_url": post_url,
        }
