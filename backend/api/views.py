from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Project, Secret
from .serializers import ProjectSerializer, SecretSerializer, UserSerializer
from django.contrib.auth.models import User
from rest_framework.decorators import action
from rest_framework.response import Response

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def rotate_secrets(self, request, pk=None):
        project = self.get_object()
        # Implement your secret rotation logic here
        return Response({'status': 'secrets rotated'})

class SecretViewSet(viewsets.ModelViewSet):
    queryset = Secret.objects.all()
    serializer = SecretSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(project_id=self.kwargs['project_pk'])

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
