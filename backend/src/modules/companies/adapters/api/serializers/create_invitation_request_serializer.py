from rest_framework import serializers

from modules.companies.domain.value_objects.membership_role import MembershipRole


class CreateInvitationRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=[role.value for role in MembershipRole])
