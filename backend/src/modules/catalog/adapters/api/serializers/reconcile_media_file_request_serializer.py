from rest_framework import serializers

from modules.catalog.domain.media_file_status import MediaFileStatus


class ReconcileMediaFileRequestSerializer(serializers.Serializer):
    machine_id = serializers.UUIDField()
    expected_version = serializers.IntegerField(min_value=1)
    status = serializers.ChoiceField(choices=[status.value for status in MediaFileStatus])
