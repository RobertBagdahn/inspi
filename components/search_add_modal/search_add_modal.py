from django_components import component


@component.register("search-add-modal")
class SearchAddModalComponent(component.Component):
    template_name = "search_add_modal/search_add_modal.html"

    def get_context_data(
        self,
        modal_id="",
        title="",
        search_placeholder="",
        search_url="",
        form_action="",
        submit_text="",
        cancel_text="",
        search_results_template="./search_results.html",
        object=None,
    ):
        return {
            "modal_id": modal_id,
            "title": title,
            "search_placeholder": search_placeholder,
            "search_url": search_url,
            "form_action": form_action,
            "submit_text": submit_text,
            "cancel_text": cancel_text,
            "search_results_template": search_results_template,
            "object": object,
        }
