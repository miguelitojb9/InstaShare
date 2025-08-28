from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from core.views import (
    CustomLoginView,
    CustomLogoutView,
    RegisterView,
    FileListView,
    FileUploadView,
    FileRenameView,
    FileDownloadView,
    ejecutar_proceso_zip
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
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_URL)