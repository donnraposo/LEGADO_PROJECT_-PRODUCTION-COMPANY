from rest_framework import serializers


class CreateProjectRequestSerializer(serializers.Serializer):
    client_id = serializers.UUIDField()
    name = serializers.CharField(max_length=160, allow_blank=False, trim_whitespace=True)
