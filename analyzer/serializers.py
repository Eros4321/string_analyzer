from rest_framework import serializers
from .models import AnalyzedString

class AnalyzeCreateSerializer(serializers.Serializer):
    value = serializers.CharField()

    def validate_value(self, v):
        if not isinstance(v, str):
            raise serializers.ValidationError("value must be a string")
        return v

class AnalyzedStringSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalyzedString
        fields = ("id", "value", "properties", "created_at")
