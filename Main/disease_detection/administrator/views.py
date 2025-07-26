from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import DatasetUploadForm
from .models import DatasetUpload
from users.views import admin_required
from django.contrib.auth.decorators import login_required

@login_required
@admin_required
def upload_dataset_view(request):
    if request.method == 'POST':
        form = DatasetUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dataset uploaded successfully!')
            return redirect('administrator:dataset_list')  
 
    else:
        form = DatasetUploadForm()
    
    return render(request, 'administrator/upload_dataset.html', {'form': form})

@login_required
@admin_required
def dataset_list_view(request):
    datasets = DatasetUpload.objects.all().order_by('-uploaded_at')
    return render(request, 'administrator/dataset_list.html', {'datasets': datasets})

@login_required
@admin_required
def delete_dataset_view(request, pk):
    dataset = get_object_or_404(DatasetUpload, pk=pk)
    dataset.zip_file.delete()  # Delete file from media folder
    dataset.delete()  # Delete record from DB
    messages.success(request, 'Dataset deleted successfully.')
    return redirect('administrator:dataset_list')