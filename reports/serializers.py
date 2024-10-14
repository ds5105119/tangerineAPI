from rest_framework import serializers

from .models import Report


class ReportSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")
    target_user = serializers.ReadOnlyField(source="target_user.username")

    class Meta:
        model = Report
        fields = ["uuid", "user", "target_type", "target_user", "description", "created_at", "resolved"]
        read_only_fields = ["uuid", "user", "created_at", "resolved"]
