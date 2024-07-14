from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Secret(models.Model):
    project = models.ForeignKey(Project, related_name='secrets', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    value = models.TextField()

    def __str__(self):
        return f"{self.name} - {self.project.name}"
