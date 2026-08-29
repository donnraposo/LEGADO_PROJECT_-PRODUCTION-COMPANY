from rest_framework import serializers


class EnsureDriveFoldersRequestSerializer(serializers.Serializer):
    project_id = serializers.UUIDField()
    date = serializers.DateField()
