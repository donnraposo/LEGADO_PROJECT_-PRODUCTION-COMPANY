import uuid

from django.db import models


class DriveOAuthStateModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    state_digest = models.CharField(max_length=64, unique=True)
    company = models.ForeignKey("companies.CompanyModel", on_delete=models.CASCADE)
    actor_user = models.ForeignKey("identity.UserProjectionModel", on_delete=models.CASCADE)
    expires_at = models.DateTimeField()
    consumed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "drive_oauth_states"
        indexes = [models.Index(fields=["expires_at"])]
