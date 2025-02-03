from django_components import component


@component.register("delete-Model")
class DeleteModelComponent(component.Component):
    template_name = "delete_model/delete_model.html"

    def get_context_data(self, id="delele", text="Sind Sie sicher, dass Sie dieses Element löschen möchten?", postUrl="", afterPostUrl=""):
        return {
            "id": id,
            "text": text,
            "postUrl": postUrl,
            "afterPostUrl": afterPostUrl,
        }
