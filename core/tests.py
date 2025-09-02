"""
Unit tests for the UploadedFile model in the core app.
This module contains a comprehensive test suite for the UploadedFile model,
covering:
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from core.models import UploadedFile


class UploadedFileModelTest(TestCase):
    """
    Test suite for the UploadedFile model.
    This class contains unit tests to verify the correct behavior of the
    UploadedFile model, including:
        - Basic creation and field assignment.
        - Automatic assignment of display_name to original_name when
            display_name is empty.
        - Calculation of file size in megabytes via get_file_size_mb method.
        - Handling of zero file size.
        - Validation of status choices.
        - String representation of the model.
        - Verification of file upload paths.
        - Timestamp fields (uploaded_at and processed_at) behavior.
    Setup creates a test user and a sample uploaded file for use in tests.
    """
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # create a simple uploaded file
        self.test_file = SimpleUploadedFile(
            "test_file.txt",
            b"file_content",
            content_type="text/plain"
        )
    
    def test_create_uploaded_file(self):
        """Test creación básica de UploadedFile"""
        uploaded_file = UploadedFile.objects.create(
            user=self.user,
            original_file=self.test_file,
            original_name="test_file.txt",
            display_name="Test File",
            file_size=1024,
            status='pending'
        )
        
        self.assertEqual(uploaded_file.original_name, "test_file.txt")
        self.assertEqual(uploaded_file.display_name, "Test File")
        self.assertEqual(uploaded_file.status, 'pending')
        self.assertEqual(uploaded_file.user, self.user)
    
    def test_display_name_defaults_to_original_name(self):
        """Test que display_name se establece automáticamente a original_name
            si está vacío"""
        uploaded_file = UploadedFile(
            user=self.user,
            original_file=self.test_file,
            original_name="original.txt",
            display_name="",
            file_size=1024
        )
        uploaded_file.save()
        
        self.assertEqual(uploaded_file.display_name, "original.txt")
    
    def test_get_file_size_mb(self):
        """Test del método get_file_size_mb"""
        # test with a file size of 2 MB (2 * 1024 * 1024 bytes)
        uploaded_file = UploadedFile.objects.create(
            user=self.user,
            original_file=self.test_file,
            original_name="test.txt",
            display_name="Test",
            file_size=2097152,  # 2 MB en bytes
            status='completed'
        )
        
        self.assertEqual(uploaded_file.get_file_size_mb(), 2.0)
    
    def test_get_file_size_mb_zero(self):
        """Test get_file_size_mb con tamaño 0"""
        uploaded_file = UploadedFile.objects.create(
            user=self.user,
            original_file=self.test_file,
            original_name="test.txt",
            display_name="Test",
            file_size=0,
            status='completed'
        )
        
        self.assertEqual(uploaded_file.get_file_size_mb(), 0)
    
    def test_status_choices(self):
        """Test que verifica las opciones de status"""
        uploaded_file = UploadedFile.objects.create(
            user=self.user,
            original_file=self.test_file,
            original_name="test.txt",
            display_name="Test",
            file_size=1024,
            status='processing'
        )
        
        # valid statuses verification
        valid_statuses = [choice[0] for choice in UploadedFile.STATUS_CHOICES]
        self.assertIn(uploaded_file.status, valid_statuses)
    
    def test_string_representation(self):
        """Test del método __str__"""
        uploaded_file = UploadedFile.objects.create(
            user=self.user,
            original_file=self.test_file,
            original_name="test.txt",
            display_name="Test File",
            file_size=1024,
            status='completed'
        )
        
        expected_str = "Test File (completed)"
        self.assertEqual(str(uploaded_file), expected_str)
    
    def test_file_upload_paths(self):
        """Test que verifica las rutas de upload"""
        uploaded_file = UploadedFile.objects.create(
            user=self.user,
            original_file=self.test_file,
            original_name="test.txt",
            display_name="Test",
            file_size=1024
        )
        
        # verification of upload paths
        self.assertTrue(uploaded_file.original_file.name.startswith(
            'media/uploads/original/')
        )
        
    def test_timestamps(self):
        """timestamp fields behavior"""
        uploaded_file = UploadedFile.objects.create(
            user=self.user,
            original_file=self.test_file,
            original_name="test.txt",
            display_name="Test",
            file_size=1024
        )
        
        self.assertIsNotNone(uploaded_file.uploaded_at)
        self.assertIsNone(uploaded_file.processed_at)
        
        # processing the file should set processed_at
        uploaded_file.status = 'completed'
        uploaded_file.save()
        
        # processed_at should still be None until explicitly set
        self.assertIsNone(uploaded_file.processed_at)