from rest_framework import serializers


class UploadCheckpointRequestSerializer(serializers.Serializer):
    confirmed_bytes = serializers.IntegerField(min_value=0)
