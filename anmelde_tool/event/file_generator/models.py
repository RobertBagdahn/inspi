import uuid
from django.contrib.auth import get_user_model
from django.db import models
from anmelde_tool.event.basic import models as event_models
from anmelde_tool.event.basic.choices import FileGenerationStatus, FileType, FileExtension
from masterdata.models import ScoutHierarchy

User = get_user_model()


# class FileTemplate(models.Model):
#     id = models.UUIDField(auto_created=True, primary_key=True, default=uuid.uuid4, editable=False)
#     file = models.FileField(storage=FileTemplateMediaStorage)
#     type = models.CharField(max_length=1, choices=FileType.choices, default=FileType.Kjp)
#     extension = models.CharField(max_length=1, choices=FileExtension.choices, default=FileExtension.Excel)
#     version = models.IntegerField(default=1)


# class GeneratedFiles(basic_models.TimeStampMixin):
#     id = models.UUIDField(auto_created=True, primary_key=True, default=uuid.uuid4, editable=False)
#     file = models.FileField(null=True, blank=True, storage=GeneratedFilesStorage)
#     error_msg = models.TextField(max_length=10000, null=True, blank=True)
#     status = models.CharField(max_length=2, choices=FileGenerationStatus.choices, default=FileGenerationStatus.Queued)
#     event = models.ForeignKey(event_models.Event, on_delete=models.CASCADE)
#     user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
#     extension = models.CharField(max_length=1, choices=FileExtension.choices, default=FileExtension.Excel)
#     template = models.ForeignKey(FileTemplate, on_delete=models.SET_NULL, null=True)
#     bund = models.ForeignKey(ScoutHierarchy, on_delete=models.SET_NULL, null=True, blank=True)
