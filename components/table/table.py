from django_components import component


@component.register("table")
class TableComponent(component.Component):
    template_name = "table/table.html"

    def get_context_data(self, page_obj=[], form=None):
        return {
            "page_obj": page_obj,
            "form": form,
        }

    class Media:
        css = "table/table.css"
        js = "table/table.js"
