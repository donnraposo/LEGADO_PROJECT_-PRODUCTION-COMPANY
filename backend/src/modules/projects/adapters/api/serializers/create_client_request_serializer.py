from rest_framework import serializers


class CreateClientRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=160, allow_blank=False, trim_whitespace=True)
