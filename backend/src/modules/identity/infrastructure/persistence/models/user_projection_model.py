import uuid

from django.db import models


class UserProjectionModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    keycloak_subject = models.CharField(max_length=255, unique=True)
    email_ciphertext = models.BinaryField()
    email_lookup_hmac = models.CharField(max_length=64, unique=True)
    is_active = models.BooleanField(default=True)
    version = models.PositiveBigIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "identity_users"
