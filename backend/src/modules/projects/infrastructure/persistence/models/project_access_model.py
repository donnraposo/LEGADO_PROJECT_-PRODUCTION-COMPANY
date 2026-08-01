import uuid

from django.db import models


class ProjectAccessModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        "projects.ProjectModel",
        on_delete=models.PROTECT,
        related_name="accesses",
    )
    user = models.ForeignKey("identity.UserProjectionModel", on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "project_accesses"
        constraints = [
            models.UniqueConstraint(fields=["project", "user"], name="uq_project_access_user")
        ]
