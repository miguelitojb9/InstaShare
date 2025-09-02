"""
API URL configuration for the core app.
Defines JWT authentication endpoints and file upload routes.
"""

from django.urls import path, include

from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from core.viewsets import UploadedFileViewSet

# Crear el router y registrar el ViewSet
router = DefaultRouter()
router.register(r'files', UploadedFileViewSet, basename='uploadedfile')

# URLs de la app
urlpatterns = [
    # Endpoints de autenticación JWT
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Incluir todas las URLs del router (CRUD de files)
    path('', include(router.urls)),
    
    # Endpoint adicional para verificar autenticación
    path('auth/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
