"""
Forms for handling file uploads and renaming in the InstaShare core app.
"""

from django import forms
from .models import UploadedFile


class FileUploadForm(forms.ModelForm):
    """
    A Django ModelForm for uploading files with an optional display name.
    Fields:
        original_file (FileField): The file to be uploaded.
        display_name (CharField, optional): An optional name to display for
        the uploaded file.
    Widgets:
        display_name: Rendered as a text input with Bootstrap styling and
        placeholder.
        original_file: Rendered as a file input with Bootstrap styling.
    Notes:
        - The 'display_name' field is not required.
    """
    class Meta:
        model = UploadedFile
        fields = ['original_file', 'display_name']
        widgets = {
            'display_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Optional display name'
            }),
            'original_file': forms.FileInput(attrs={
                'class': 'form-control'
            })
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['display_name'].required = False


class FileRenameForm(forms.ModelForm):
    """
    A Django ModelForm for renaming an uploaded file.

    This form allows users to update the `display_name` field of an
    `UploadedFile` instance.
    It uses a text input widget styled with the 'form-control' CSS class
    for better UI integration.

    Meta:
        model (UploadedFile): The model associated with this form.
        fields (list): Specifies that only the 'display_name' field
        editable.
        widgets (dict): Customizes the widget for 'display_name' to use a
        styled text input.
    """
    class Meta:
        model = UploadedFile
        fields = ['display_name']
        widgets = {
            'display_name': forms.TextInput(attrs={
                'class': 'form-control'
            })
        }