from rest_framework import serializers


class AcceptInvitationRequestSerializer(serializers.Serializer):
    token = serializers.CharField(min_length=32, max_length=256, trim_whitespace=True)
