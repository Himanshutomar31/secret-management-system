from rest_framework import serializers
from .models import Project, Secret
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class SecretSerializer(serializers.ModelSerializer):
    class Meta:
        model = Secret
        fields = ['id', 'name', 'value', 'project']

class ProjectSerializer(serializers.ModelSerializer):
    secrets = SecretSerializer(many=True, read_only=True)
    
    class Meta:
        model = Project
        fields = ['id', 'name', 'secrets']
