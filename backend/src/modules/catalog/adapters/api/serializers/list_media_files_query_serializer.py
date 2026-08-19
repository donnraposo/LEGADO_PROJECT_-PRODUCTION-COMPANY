from rest_framework import serializers


class ListMediaFilesQuerySerializer(serializers.Serializer):
    q = serializers.CharField(required=False, allow_blank=True, max_length=200, default="")
    project_id = serializers.UUIDField(required=False)
    status = serializers.CharField(required=False, allow_blank=True, max_length=40, default="")
    tag_id = serializers.UUIDField(required=False)
    extension = serializers.CharField(required=False, allow_blank=True, max_length=32, default="")
    media_type = serializers.CharField(required=False, allow_blank=True, max_length=120, default="")
    min_size_bytes = serializers.IntegerField(required=False, min_value=0)
    max_size_bytes = serializers.IntegerField(required=False, min_value=0)
    recorded_from = serializers.DateTimeField(required=False)
    recorded_to = serializers.DateTimeField(required=False)
    created_by_user_id = serializers.UUIDField(required=False)
    cursor = serializers.CharField(required=False, max_length=64)
    limit = serializers.IntegerField(required=False, min_value=1, max_value=100, default=50)

    def validate(self, attrs):
        if (
            attrs.get("min_size_bytes") is not None
            and attrs.get("max_size_bytes") is not None
            and attrs["min_size_bytes"] > attrs["max_size_bytes"]
        ):
            raise serializers.ValidationError("O tamanho mínimo excede o máximo.")
        if (
            attrs.get("recorded_from")
            and attrs.get("recorded_to")
            and attrs["recorded_from"] > attrs["recorded_to"]
        ):
            raise serializers.ValidationError("A data inicial excede a final.")
        return attrs
