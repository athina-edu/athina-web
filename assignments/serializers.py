from rest_framework import serializers
from assignments.models import Assignment
from django.conf import settings
import git


class AssignmentListSerializer(serializers.ModelSerializer):
    """Serializer to map the Model instance into JSON format."""
    directory = serializers.SerializerMethodField()

    def get_directory(self, obj):
        # FIXME: This guarantees updated repos whenever athina needs them, but, extreme if pulling too many dirs
        # Refresh git directories in case there have been any changes
        try:
            git.Repo('%s/%s/' % (settings.BASE_DIR, obj.absolute_path)).remote().pull()
        except git.exc.InvalidGitRepositoryError:  # this exception should never happen unless someone messed with repos
            pass

        # Return directory
        return '%s/%s/' % (settings.BASE_DIR, obj.absolute_path)

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = Assignment
        fields = ('directory', 'simulate')
