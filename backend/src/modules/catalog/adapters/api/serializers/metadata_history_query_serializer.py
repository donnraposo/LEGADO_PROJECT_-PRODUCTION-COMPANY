from rest_framework import serializers


class MetadataHistoryQuerySerializer(serializers.Serializer):
    after_version = serializers.IntegerField(required=False, min_value=0, default=0)
    limit = serializers.IntegerField(required=False, min_value=1, max_value=100, default=50)
