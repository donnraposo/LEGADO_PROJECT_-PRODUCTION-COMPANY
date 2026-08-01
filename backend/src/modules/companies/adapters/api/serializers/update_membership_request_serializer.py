from rest_framework import serializers

from modules.companies.domain.value_objects.membership_role import MembershipRole
from modules.companies.domain.value_objects.membership_status import MembershipStatus


class UpdateMembershipRequestSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=[role.value for role in MembershipRole], required=False)
    status = serializers.ChoiceField(
        choices=[status.value for status in MembershipStatus], required=False
    )
