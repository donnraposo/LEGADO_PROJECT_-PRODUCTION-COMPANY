from rest_framework import serializers


class UpdateMediaMetadataRequestSerializer(serializers.Serializer):
    expected_version = serializers.IntegerField(min_value=1)
    display_name = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(allow_blank=True, required=False)
    observations = serializers.CharField(allow_blank=True, required=False)
    recorded_at = serializers.DateTimeField(allow_null=True, required=False)
