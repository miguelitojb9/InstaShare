import zipfile
import os
from django.core.management.base import BaseCommand
from core.models import UploadedFile
from django.conf import settings
# from decouple import config, Csv


class Command(BaseCommand):
    """
    Django management command to process pending uploaded files by compressing
    them into ZIP archives.
    This command performs the following steps for each file with status
    'pending':
    1. Updates the file status to 'processing'.
    2. Compresses the original file into a ZIP archive stored in the
    'uploads/compressed' directory.
    3. Updates the file's compressed_file field and sets status to 'completed'
    upon success.
    4. Handles errors by setting the file status to 'failed' and logging the
    error.
    Outputs progress and status messages to the console.
    """
    help = 'Process pending files by compressing them'
    
    def handle(self, *args, **options):
        # Get all pending files
        pending_files = UploadedFile.objects.filter(status='pending')
        
        self.stdout.write(f"Found {pending_files.count()} files to process")
        
        if pending_files:
            for file in pending_files:
                try:
                    # Update status to processing
                    file.status = 'processing'
                    file.save()
                    
                    self.stdout.write(f"Processing file: {file.display_name}")
                    
                    # Create compressed version
                    original_path = file.original_file.path
                    compressed_filename = f"{file.display_name}.zip"
                    compressed_path = os.path.join(
                        settings.MEDIA_ROOT,
                        'media/uploads/compressed',
                        compressed_filename
                    )
                    
                    # Ensure directory exists
                    os.makedirs(os.path.dirname(compressed_path), exist_ok=True)
                    
                    # Create zip file
                    with zipfile.ZipFile(
                        compressed_path,
                        'w',
                        zipfile.ZIP_DEFLATED
                    ) as zipf:
                        zipf.write(original_path, os.path.basename(original_path))
                    
                    # Update model
                    file.compressed_file.name = f'media/uploads/compressed/{compressed_filename}'
                    file.status = 'completed'
                    file.save()
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Successfully processed file {file.display_name}'
                        )
                    )
                    
                except Exception as e:
                    file.status = 'failed'
                    file.save()
                    self.stdout.write(self.style.ERROR(
                        f'Error processing file {file.display_name}: {str(e)}')
                    )