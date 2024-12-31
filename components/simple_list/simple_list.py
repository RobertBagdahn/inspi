from django_components import component


@component.register("simple-list")
class SimpleListComponent(component.Component):
    template_name = "simple_list/simple_list.html"

    def get_context_data(
        self,
        items=[],
    ):
        return {
            "items": items,
        }