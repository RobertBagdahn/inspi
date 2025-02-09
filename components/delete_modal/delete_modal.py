from django_components import component


@component.register("delete-modal")
class DeleteModelComponent(component.Component):
    template_name = "delete_modal/delete_modal.html"

    def get_context_data(self, id="delele", text="Sind Sie sicher, dass Sie dieses Element löschen möchten?", post_url="", after_post_url=""):
        return {
            "id": id,
            "text": text,
            "post_url": post_url,
            "after_post_url": after_post_url,
        }
