"""
Viewsets and API endpoints for managing uploaded files in InstaShare core.
Includes file upload, processing, download, batch processing, and statistics.
"""

import os
import zipfile
from datetime import datetime

from django.conf import settings

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import UploadedFile
from .serializers import UploadedFileSerializer, UploadedFileCreateSerializer


class UploadedFileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing uploaded files.
    This viewset provides endpoints for:
    - Listing and retrieving files uploaded by the authenticated user.
    - Creating new file uploads, automatically associating them with the
    current user.
    - Processing an uploaded file via a custom action (`process_file`), which
    sets its status to 'processing'.
    - Downloading the original uploaded file (`download_original`).
    - Downloading the compressed version of the file (`download_compressed`),
    if available.
    Permissions:
        Only authenticated users can access these endpoints.
    Serializers:
        Uses different serializers for creation and other actions.
    Actions:
        - process_file: POST, triggers processing logic for a specific file.
        - download_original: GET, returns the download URL for the original
        file.
        - download_compressed: GET, returns the download URL for the
        compressed file, if it exists.
    Queryset:
        Only files belonging to the current user are accessible.
    """
    queryset = UploadedFile.objects.all()
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UploadedFileCreateSerializer
        return UploadedFileSerializer
    
    def get_queryset(self):
        return UploadedFile.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def process_file(self, request, pk=None):
        """Procesar un archivo específico"""
        uploaded_file = self.get_object()
        
        try:
            # Actualizar estado a procesando
            uploaded_file.status = 'processing'
            uploaded_file.save()
            
            # Crear versión comprimida
            original_path = uploaded_file.original_file.path
            compressed_filename = f"compressed_{uploaded_file.original_name}.zip"
            compressed_path = os.path.join(
                settings.MEDIA_ROOT,
                'uploads/compressed',
                compressed_filename
            )
            
            # Asegurar que el directorio existe
            os.makedirs(os.path.dirname(compressed_path), exist_ok=True)
            
            # Crear archivo zip
            with zipfile.ZipFile(
                compressed_path,
                'w',
                zipfile.ZIP_DEFLATED
            ) as zipf:
                zipf.write(original_path, os.path.basename(original_path))
            
            # Actualizar modelo
            uploaded_file.compressed_file.name = f'uploads/compressed/{compressed_filename}'
            uploaded_file.status = 'completed'
            uploaded_file.processed_at = datetime.now()
            uploaded_file.save()
            
            return Response({
                'status': 'success',
                'message': f'File {uploaded_file.display_name} processed successfully',
                'compressed_file_url': uploaded_file.compressed_file.url
            })
            
        except Exception as e:
            uploaded_file.status = 'failed'
            uploaded_file.save()
            return Response({
                'status': 'error',
                'message': f'Error processing file {uploaded_file.display_name}: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def download_original(self, request, pk=None):
        uploaded_file = self.get_object()
        return Response({
            'download_url': uploaded_file.original_file.url
        })
    
    @action(detail=True, methods=['get'])
    def download_compressed(self, request, pk=None):
        uploaded_file = self.get_object()
        if not uploaded_file.compressed_file:
            return Response(
                {'error': 'No compressed file available'},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response({
            'download_url': uploaded_file.compressed_file.url
        })


class ProcessFilesView(APIView):
    """Endpoint para procesar todos los archivos pendientes"""
    permission_classes = [IsAuthenticated]  # Solo administradores
    
    def post(self, request):
        try:
            # Obtener todos los archivos pendientes
            pending_files = UploadedFile.objects.filter(status='pending')
            
            results = {
                'total_files': pending_files.count(),
                'processed': 0,
                'failed': 0,
                'details': []
            }
            
            if pending_files:
                for file in pending_files:
                    try:
                        # Actualizar estado a procesando
                        file.status = 'processing'
                        file.save()
                        
                        # Crear versión comprimida
                        original_path = file.original_file.path
                        compressed_filename = f"compressed_{file.original_name}.zip"
                        compressed_path = os.path.join(
                            settings.MEDIA_ROOT,
                            'uploads/compressed',
                            compressed_filename
                        )
                        
                        # Asegurar que el directorio existe
                        os.makedirs(os.path.dirname(compressed_path), exist_ok=True)
                        
                        # Crear archivo zip
                        with zipfile.ZipFile(
                            compressed_path,
                            'w',
                            zipfile.ZIP_DEFLATED
                        ) as zipf:
                            zipf.write(original_path, os.path.basename(original_path))
                        
                        # Actualizar modelo
                        file.compressed_file.name = f'uploads/compressed/{compressed_filename}'
                        file.status = 'completed'
                        file.processed_at = datetime.now()
                        file.save()
                        
                        results['processed'] += 1
                        results['details'].append({
                            'file_id': file.id,
                            'file_name': file.display_name,
                            'status': 'success',
                            'compressed_url': file.compressed_file.url
                        })
                        
                    except Exception as e:
                        file.status = 'failed'
                        file.save()
                        results['failed'] += 1
                        results['details'].append({
                            'file_id': file.id,
                            'file_name': file.display_name,
                            'status': 'error',
                            'error': str(e)
                        })
            
            return Response({
                'status': 'completed',
                'summary': results,
                'message': f'Processed {results["processed"]} files, {results["failed"]} failed'
            })
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Error in batch processing: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FileStatsView(APIView):
    """Endpoint para estadísticas de archivos"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user_files = UploadedFile.objects.filter(user=request.user)
        
        total_files = user_files.count()
        total_size_mb = sum(file.get_file_size_mb() for file in user_files)
        
        files_by_status = {
            status: user_files.filter(status=status).count()
            for status in ['pending', 'processing', 'completed', 'failed']
        }
        
        # Archivos pendientes de procesar
        pending_files = user_files.filter(status='pending')
        pending_list = [
            {
                'id': file.id,
                'name': file.display_name,
                'uploaded_at': file.uploaded_at,
                'size_mb': file.get_file_size_mb()
            }
            for file in pending_files
        ]
        
        return Response({
            'total_files': total_files,
            'total_size_mb': round(total_size_mb, 2),
            'files_by_status': files_by_status,
            'pending_files': pending_list
        })