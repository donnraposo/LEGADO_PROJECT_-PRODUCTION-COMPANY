from rest_framework import serializers


class UploadSessionRequestSerializer(serializers.Serializer):
    machine_id = serializers.UUIDField()
