"""
Serializers for User and UploadedFile models in the InstaShare core app.
Provides representations and validation for user and file upload data.
"""

from rest_framework import serializers
from django.contrib.auth.models import User

from .models import UploadedFile


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.

    Serializes the following fields:
        - id: Unique identifier for the user.
        - username: The user's username.
        - email: The user's email address.

    Inherits from:
        serializers.ModelSerializer
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class UploadedFileSerializer(serializers.ModelSerializer):
    """
    Serializer for the UploadedFile model, providing representation and
    validation for uploaded file instances.
    Fields:
        - id: Unique identifier for the uploaded file (read-only).
        - user: Serialized user who uploaded the file (read-only).
        - original_file: The original uploaded file.
        - compressed_file: The compressed version of the uploaded file.
        - original_name: The original name of the uploaded file.
        - display_name: The display name for the file.
        - file_size: Size of the original file in bytes (read-only).
        - file_size_mb: Size of the original file in megabytes, calculated via
        get_file_size_mb (read-only).
        - status: Processing status of the file (read-only).
        - uploaded_at: Timestamp when the file was uploaded (read-only).
        - processed_at: Timestamp when the file was processed (read-only).
    Methods:
        - get_file_size_mb(obj): Returns the file size in megabytes for the
        given UploadedFile instance.
    """
    user = UserSerializer(read_only=True)
    file_size_mb = serializers.SerializerMethodField()
    
    class Meta:
        model = UploadedFile
        fields = [
            'id', 'user', 'original_file', 'compressed_file',
            'original_name', 'display_name', 'file_size', 'file_size_mb',
            'status', 'uploaded_at', 'processed_at'
        ]
        read_only_fields = [
            'id', 'user', 'file_size', 'file_size_mb',
            'status', 'uploaded_at', 'processed_at'
        ]
    
    def get_file_size_mb(self, obj):
        return obj.get_file_size_mb()


class UploadedFileCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating UploadedFile instances.
    This serializer handles the creation of UploadedFile objects, including setting
    the user, original file, original name, display name, and file size. The
    display name defaults to the file's name if not provided.
    Fields:
        - original_file: The uploaded file.
        - display_name: Optional display name for the file.
    Methods:
        - create(validated_data): Creates and saves an UploadedFile instance using
          the validated data and the request user from the serializer context.
    """
    class Meta:
        model = UploadedFile
        fields = ['original_file', 'display_name']
    
    def create(self, validated_data):
        request = self.context.get('request')
        file = validated_data['original_file']
        
        uploaded_file = UploadedFile(
            user=request.user,
            original_file=file,
            original_name=file.name,
            display_name=validated_data.get('display_name', file.name),
            file_size=file.size
        )
        uploaded_file.save()
        return uploaded_file