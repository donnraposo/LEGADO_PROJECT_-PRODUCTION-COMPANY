from rest_framework import serializers


class UploadBatchItemRequestSerializer(serializers.Serializer):
    file_version_id = serializers.UUIDField()
    destination_category = serializers.ChoiceField(choices=["ORIGINAIS", "PREVIEWS", "ENTREGAS"])
    final_name = serializers.CharField(min_length=1, max_length=255, trim_whitespace=True)


class UploadBatchRequestSerializer(serializers.Serializer):
    project_id = serializers.UUIDField()
    machine_id = serializers.UUIDField()
    folder_date = serializers.DateField()
    idempotency_key = serializers.CharField(min_length=8, max_length=120)
    items = UploadBatchItemRequestSerializer(many=True, min_length=1, max_length=10000)
