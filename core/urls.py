"""
URL configuration for the core app of InstaShare.
Defines routes for authentication, file operations, batch processing,
statistics, and API documentation.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

from core.viewsets import FileStatsView, ProcessFilesView

from core.views import (
    CustomLoginView,
    CustomLogoutView,
    RegisterView,
    FileListView,
    FileUploadView,
    FileRenameView,
    FileDownloadView,
    ejecutar_proceso_zip,
)

urlpatterns = [
    path('', FileListView.as_view(), name='file_list'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('upload/', FileUploadView.as_view(), name='upload'),
    path('rename/<int:file_id>/', FileRenameView.as_view(), name='rename'),
    path(
            'download/<int:file_id>/',
            FileDownloadView.as_view(),
            name='download'
        ),
    path(
            'api/ejecutar-proceso-zip/',
            ejecutar_proceso_zip,
            name='ejecutar_proceso_zip'
        ),
    
    # Endpoint para procesamiento batch
    path('process-files/', ProcessFilesView.as_view(), name='process_files'),
    
    # Endpoint para estadísticas
    path('stats/', FileStatsView.as_view(), name='file_stats'),
    path('api/', include('core.api_urls')),  # Incluye las URLs de tu app
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_URL)