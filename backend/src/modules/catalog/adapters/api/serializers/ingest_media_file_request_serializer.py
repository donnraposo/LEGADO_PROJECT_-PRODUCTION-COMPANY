from rest_framework import serializers


class IngestMediaFileRequestSerializer(serializers.Serializer):
    project_id = serializers.UUIDField()
    machine_id = serializers.UUIDField()
    ingestion_id = serializers.UUIDField()
    original_name = serializers.CharField(max_length=255)
    media_type = serializers.CharField(max_length=120, allow_blank=True, required=False)
    size_bytes = serializers.IntegerField(min_value=0)
    checksum_algorithm = serializers.CharField(max_length=24)
    checksum_digest = serializers.CharField(max_length=128)
    recorded_at = serializers.DateTimeField(allow_null=True, required=False)
