from django.shortcuts import render
import subprocess
import os
import logging
from django.views.generic import ListView, CreateView, UpdateView, View
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from core.models import UploadedFile
from .forms import FileUploadForm, FileRenameForm
from django.views.decorators.http import require_POST
from django.conf import settings


class CustomLoginView(LoginView):
    """
    Custom login view that extends Django's LoginView.
    Attributes:
        template_name (str): Path to the template used for rendering the login
        page.
        redirect_authenticated_user (bool): If True, authenticated users are
        redirected instead of seeing the login page.
    """
    template_name = 'registration/login.html'
    redirect_authenticated_user = True


class CustomLogoutView(LogoutView):
    """
    Custom logout view that redirects users to the login page after logging
    out.
    Inherits from Django's built-in LogoutView and sets the `next_page`
    attribute
    to the URL named 'login', ensuring users are redirected appropriately.
    """
    next_page = reverse_lazy('login')


class RegisterView(View):
    """
    View for handling user registration.
    Methods:
        get(request):
            Handles GET requests. Renders the registration form for new users.
        post(request):
            Handles POST requests. Processes the submitted registration form.
            If the form is valid, creates a new user, logs them in, and
            redirects to the file list page.
            If the form is invalid, re-renders the registration form with
            errors.
    """
    def get(self, request):
        
        form = UserCreationForm()
        return render(request, 'registration/register.html', {'form': form})
    
    def post(self, request):
        """
        Handles POST requests for user registration.

        Processes the submitted registration form. If the form is valid,
        creates a new user,
        logs them in, and redirects to the file list page. If the form is
        invalid, re-renders
        the registration page with form errors.

        Args:
            request (HttpRequest): The HTTP request object containing POST
            data.

        Returns:
            HttpResponse: Redirects to 'file_list' on successful registration,
            or renders
            the registration template with form errors on failure.
        """
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('file_list')
        return render(request, 'registration/register.html', {'form': form})


class FileListView(LoginRequiredMixin, ListView):
    """
    View for displaying a list of files uploaded by the currently
    authenticated user.
    Inherits from:
        LoginRequiredMixin: Ensures that only logged-in users can access the
        view.
        ListView: Provides generic functionality for displaying a list of
        objects.
    Attributes:
        model (UploadedFile): The model representing uploaded files.
        template_name (str): The template used to render the file list.
        context_object_name (str): The name of the context variable for the
        list of files.
    Methods:
        get_queryset(): Returns a queryset of UploadedFile objects filtered by
        the current user, ordered by upload date in descending order.
    """
    model = UploadedFile
    template_name = 'file_list.html'
    context_object_name = 'files'
    
    def get_queryset(self):
        return UploadedFile.objects.filter(
                user=self.request.user
            ).order_by('-uploaded_at')


class FileUploadView(LoginRequiredMixin, CreateView):
    """
    View for handling file uploads by authenticated users.
    Inherits from Django's CreateView and LoginRequiredMixin to ensure only
    logged-in users can upload files.
    Uses the UploadedFile model and FileUploadForm for file data.
    On successful form submission, associates the uploaded file with the
    current user, stores the original filename and file size,
    and sets the display name to the original filename if not provided.
    Attributes:
        model (UploadedFile): The model used for storing uploaded files.
        form_class (FileUploadForm): The form class for file uploads.
        template_name (str): The template used for rendering the upload page.
        success_url (str): The URL to redirect to after a successful upload.
    Methods:
        form_valid(form): Processes the form data before saving, setting user,
        original name, file size, and display name.
    """
    model = UploadedFile
    form_class = FileUploadForm
    template_name = 'upload.html'
    success_url = reverse_lazy('file_list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.original_name = self.request.FILES['original_file'].name
        form.instance.file_size = self.request.FILES['original_file'].size
        # Si no se proporciona un nombre de visualización, usar el nombre
        # original
        if not form.instance.display_name:
            form.instance.display_name = form.instance.original_name
                    
        return super().form_valid(form)


class FileRenameView(LoginRequiredMixin, UpdateView):
    """
    View for renaming an uploaded file.
    This view allows authenticated users to rename files they have uploaded.
    It uses the `FileRenameForm` to handle the renaming process and restricts
    access to files owned by the current user. Upon successful renaming, the
    user is redirected to the file list page.
    Attributes:
        model (UploadedFile): The model representing the uploaded file.
        form_class (FileRenameForm): The form used for renaming files.
        template_name (str): The template used to render the rename form.
        success_url (str): The URL to redirect to after a successful rename.
        pk_url_kwarg (str): The keyword argument for the file's primary key.
    Methods:
        get_queryset(): Returns a queryset of files owned by the current user.
    """
    model = UploadedFile
    form_class = FileRenameForm
    template_name = 'rename.html'
    success_url = reverse_lazy('file_list')
    pk_url_kwarg = 'file_id'
    context_object_name = 'file'
    
    def get_queryset(self):
        return UploadedFile.objects.filter(user=self.request.user)


class FileDownloadView(LoginRequiredMixin, View):
    """
    View for handling the download of compressed files uploaded by users.
    This view requires the user to be authenticated. It retrieves the requested file
    by its ID and ensures that the file belongs to the requesting user. If the file's
    status is not 'completed', it returns a 400 response indicating the file is not
    ready for download. Otherwise, it serves the compressed file as a ZIP attachment.
    Methods:
        get(request, *args, **kwargs): Handles GET requests to download the file.
            - Returns a ZIP file if available and completed.
            - Returns a 400 error if the file is not ready.
    """
    def get(self, request, *args, **kwargs):
        file_instance = get_object_or_404(
            UploadedFile,
            id=kwargs['file_id'],
            user=request.user
        )
        
        if file_instance.status != 'completed':
            return HttpResponse("File is not ready for download", status=400)
        
        response = HttpResponse(
            file_instance.compressed_file,
            content_type='application/zip'
        )
        response['Content-Disposition'] = (
            f'attachment; filename="{file_instance.display_name}.zip"'
        )
        return response
    
    
logger = logging.getLogger(__name__)


@require_POST
@csrf_exempt  # Solo  desarrollo; en producción, usar token CSRF adecuado
def ejecutar_proceso_zip(request):
    """
    Executes a custom Django management command ('process_files') using a
    subprocess.
    This view runs the 'process_files' command via manage.py, captures its
    output,
    and returns a JSON response indicating success or failure. Handles
    timeouts and
    unexpected errors gracefully.
    Args:
        request (HttpRequest): The HTTP request object.
    Returns:
        JsonResponse: A JSON response containing the result of the command
        execution.
            - On success: {'success': True, 'message': str, 'output': str}
            - On failure: {'success': False, 'error': str, 'output': str}
            - On timeout or exception: {'error': str}
    Exceptions:
        subprocess.TimeoutExpired: If the command execution exceeds the
        timeout.
        Exception: For any other unexpected errors.
    """
    try:
        # Ruta al manage.py
        manage_py_path = os.path.join(settings.BASE_DIR, 'manage.py')
        
        # Ejecutar el comando personalizado
        resultado = subprocess.run(
            ['python', manage_py_path, 'process_files'],
            capture_output=True,
            text=True, timeout=300,
            cwd=settings.BASE_DIR,
            check=False
        )
        
        if resultado.returncode == 0:
            logger.info(f"Comando ejecutado exitosamente: {resultado.stdout}")
            return JsonResponse({
                'success': True,
                'message': 'Proceso de archivos completado',
                'output': resultado.stdout
            })
        else:
            logger.error(f"Error en comando: {resultado.stderr}")
            return JsonResponse({
                'success': False,
                'error': resultado.stderr,
                'output': resultado.stdout
            }, status=500)
            
    except subprocess.TimeoutExpired:
        logger.error("Tiempo de espera agotado")
        return JsonResponse({'error': 'Tiempo de espera agotado'}, status=500)
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)