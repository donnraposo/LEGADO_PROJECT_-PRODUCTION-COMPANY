from rest_framework import serializers


class UploadControlRequestSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=["PAUSE", "RESUME", "CANCEL"])
    expected_version = serializers.IntegerField(min_value=1)
    idempotency_key = serializers.CharField(min_length=8, max_length=120)
