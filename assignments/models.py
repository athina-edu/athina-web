from django.db import models
from django.utils import timezone


class Assignment(models.Model):
    name = models.CharField(max_length=200, unique=True)
    absolute_path = models.CharField(max_length=200, editable=False)
    owner = models.IntegerField(editable=False, default=1)
    date_created = models.DateTimeField('Date Created', default=timezone.now, editable=False)
    data_updated = models.DateTimeField('Date Updated', auto_now=True)
    active = models.BooleanField(default=True)
    simulate = models.BooleanField(default=True)
    git_source = models.CharField(max_length=255, default="")
    git_username = models.CharField(max_length=255, default="", blank=True)
    git_password = models.CharField(max_length=255, default="", blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        keep_characters = (' ', '.', '_', '-')
        self.name = "".join(c for c in self.name if c.isalnum() or c in keep_characters).rstrip()
        super(Assignment, self).save(*args, **kwargs)
