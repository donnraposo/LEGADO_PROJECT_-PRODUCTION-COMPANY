import uuid

from django.db import models


class ProjectModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey("companies.CompanyModel", on_delete=models.PROTECT)
    client = models.ForeignKey("projects.ClientModel", on_delete=models.PROTECT)
    name = models.CharField(max_length=160)
    normalized_name = models.CharField(max_length=160)
    created_by_user = models.ForeignKey("identity.UserProjectionModel", on_delete=models.PROTECT)
    archived_at = models.DateTimeField(null=True, blank=True)
    version = models.PositiveBigIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "projects"
        ordering = ["name", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["client", "normalized_name"], name="uq_project_client_name"
            )
        ]
