import uuid

from django.db import models

from modules.companies.domain.value_objects.membership_role import MembershipRole


class InvitationModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        "companies.CompanyModel",
        on_delete=models.PROTECT,
        related_name="invitations",
    )
    email_ciphertext = models.BinaryField()
    email_lookup_hmac = models.CharField(max_length=64)
    token_digest = models.CharField(max_length=64, unique=True)
    role = models.CharField(
        max_length=20,
        choices=[(role.value, role.value) for role in MembershipRole],
    )
    invited_by_user = models.ForeignKey(
        "identity.UserProjectionModel",
        on_delete=models.PROTECT,
        related_name="sent_company_invitations",
    )
    expires_at = models.DateTimeField()
    accepted_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "company_invitations"
        ordering = ["-created_at", "id"]
