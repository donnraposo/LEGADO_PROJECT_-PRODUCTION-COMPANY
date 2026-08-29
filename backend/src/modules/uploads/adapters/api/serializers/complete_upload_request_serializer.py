from rest_framework import serializers


class CompleteUploadRequestSerializer(serializers.Serializer):
    machine_id = serializers.UUIDField()
    provider_object_id = serializers.CharField(min_length=1, max_length=255)
