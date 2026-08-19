from rest_framework import serializers


class RestoreMetadataRequestSerializer(serializers.Serializer):
    expected_version = serializers.IntegerField(min_value=1)
