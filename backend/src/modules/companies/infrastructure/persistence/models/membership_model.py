import uuid

from django.db import models

from modules.companies.domain.value_objects.membership_role import MembershipRole
from modules.companies.domain.value_objects.membership_status import MembershipStatus


class MembershipModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        "companies.CompanyModel",
        on_delete=models.PROTECT,
        related_name="memberships",
    )
    user = models.ForeignKey(
        "identity.UserProjectionModel",
        on_delete=models.PROTECT,
        related_name="memberships",
    )
    role = models.CharField(
        max_length=20,
        choices=[(role.value, role.value) for role in MembershipRole],
    )
    status = models.CharField(
        max_length=16,
        choices=[(status.value, status.value) for status in MembershipStatus],
        default=MembershipStatus.ACTIVE.value,
    )
    version = models.PositiveBigIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "company_memberships"
        constraints = [
            models.UniqueConstraint(
                fields=["company", "user"],
                name="uq_company_membership_user",
            )
        ]
