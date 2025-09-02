"""
Models for core app: defines UploadedFile for user file uploads and processing.
"""

from django.contrib.auth.models import User
from django.db import models


class UploadedFile(models.Model):
    """
    Model representing a file uploaded by a user, including its original and
    compressed versions,
    metadata, and processing status.
    Attributes:
        STATUS_CHOICES (tuple): Possible statuses for the file processing
        workflow.
        user (ForeignKey): Reference to the user who uploaded the file.
        original_file (FileField): The original uploaded file.
        compressed_file (FileField): The compressed version of the file
        (optional).
        original_name (CharField): The original name of the uploaded file.
        display_name (CharField): The name to display for the file.
        file_size (BigIntegerField): Size of the original file in bytes.
        status (CharField): Current processing status of the file.
        uploaded_at (DateTimeField): Timestamp when the file was uploaded.
        processed_at (DateTimeField): Timestamp when the file was processed
        (optional).
    Methods:
        __str__(): Returns a string representation of the file with its
        display name and status.
        save(*args, **kwargs): Ensures display_name is set to original_name
        if not provided before saving.
        get_file_size_mb(): Returns the file size in megabytes, rounded to
        two decimal places.
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    original_file = models.FileField(upload_to='media/uploads/original/')
    compressed_file = models.FileField(
        upload_to='media/uploads/compressed/',
        null=True,
        blank=True)
    original_name = models.CharField(max_length=255)
    display_name = models.CharField(max_length=255)
    file_size = models.BigIntegerField()  # Tamaño en bytes
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.display_name} ({self.status})"
    
    def save(self, *args, **kwargs):
        if not self.display_name:
            self.display_name = self.original_name
        super().save(*args, **kwargs)
    
    def get_file_size_mb(self):
        """
        Returns the file size in megabytes (MB), rounded to two decimal places.

        If the file size is not set, returns 0.

        Returns:
            float: The file size in MB, rounded to two decimals, or 0 if file size is None or zero.
        """
        return round(
            self.file_size / (1024 * 1024), 2
            ) if self.file_size else 0