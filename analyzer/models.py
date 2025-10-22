from django.db import models
from django.utils import timezone

class AnalyzedString(models.Model):
    """
    Primary key is SHA-256 hash of the string value for unique identification.
    We store 'properties' as JSON so searches/filters can inspect precomputed data.
    """
    id = models.CharField(max_length=64, primary_key=True)  # sha256 hex digest
    value = models.TextField(unique=True)
    properties = models.JSONField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.id} - {self.value[:40]}"
