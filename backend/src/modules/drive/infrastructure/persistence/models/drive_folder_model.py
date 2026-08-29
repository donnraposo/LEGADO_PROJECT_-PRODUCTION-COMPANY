import uuid

from django.db import models


class DriveFolderModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey(
        "drive.DriveAccountModel",
        on_delete=models.PROTECT,
        related_name="folders",
    )
    project = models.ForeignKey(
        "projects.ProjectModel",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="drive_folders",
    )
    folder_key = models.CharField(max_length=255)
    provider_folder_id = models.CharField(max_length=255)
    parent_provider_folder_id = models.CharField(max_length=255, blank=True)
    name = models.CharField(max_length=160)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "drive_folders"
        constraints = [
            models.UniqueConstraint(
                fields=["account", "folder_key"],
                name="uq_drive_folder_account_key",
            )
        ]
