from rest_framework import serializers
from assignments.models import Assignment
from django.conf import settings


class AssignmentListSerializer(serializers.ModelSerializer):
    """Serializer to map the Model instance into JSON format."""
    directory = serializers.SerializerMethodField()

    def get_directory(self, obj):
        return '%s/%s/' % (settings.BASE_DIR, obj.absolute_path)

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = Assignment
        fields = ('directory', 'simulate')
