from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, SecretViewSet, UserViewSet

router = DefaultRouter()
router.register(r'projects', ProjectViewSet)
router.register(r'projects/(?P<project_pk>[^/.]+)/secrets', SecretViewSet, basename='project-secrets')
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
