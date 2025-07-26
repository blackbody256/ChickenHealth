import json
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from users.models import User  
from administrator.models import DatasetUpload
from diagnosis.models import Diagnosis
from django.db.models import Count, Avg
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib import messages 
import os
from django.conf import settings
from .forms import VetUploadForm
from .models import VetUpload
import pandas as pd 
import zipfile


@login_required
def dashboard(request):
    if request.user.role != 'VET':
        return render(request, '403.html')

    # Stats
    num_farmers = User.objects.filter(role='FARMER').count()
    num_diagnoses = Diagnosis.objects.filter(user=request.user).count()
    num_uploads = VetUpload.objects.filter(user=request.user).count()

    # Recent activities
    from django.utils.timezone import now
    recent_activities = []

    recent_diagnoses = Diagnosis.objects.filter(user=request.user).order_by('-timestamp')[:3]
    for diag in recent_diagnoses:
        recent_activities.append({
            'type': 'Diagnosis',
            'title': diag.disease_name,
            'detail': 'Diagnosis submitted',
            'time': diag.timestamp,
            'badge': 'blue'
        })

    recent_uploads = VetUpload.objects.filter(user=request.user).order_by('-uploaded_at')[:3]
    for upload in recent_uploads:
        recent_activities.append({
            'type': 'Upload',
            'title': upload.title,
            'detail': 'File uploaded',
            'time': upload.uploaded_at,
            'badge': 'green'
        })

    recent_activities.sort(key=lambda x: x['time'], reverse=True)

    # Activity Score
    upload_score = min(num_uploads * 5, 30)
    diagnosis_score = min(num_diagnoses * 2, 40)
    activity_score = upload_score + diagnosis_score

    # ✅ NOW create the context
    context = {
        'num_farmers': num_farmers,
        'num_diagnoses': num_diagnoses,
        'num_uploads': num_uploads,
        'recent_activities': recent_activities,
        'upload_score': upload_score,
        'diagnosis_score': diagnosis_score,
        'activity_score': activity_score
    }

    return render(request, 'vet/dashboard.html', context)




@login_required
def dataset_list(request):
    if request.user.role != 'VET':
        messages.error(request, "Access denied.")
        return redirect('vet:dashboard')

    datasets = DatasetUpload.objects.all().order_by('-uploaded_at')
    uploads = VetUpload.objects.filter(user=request.user).order_by('-uploaded_at')

    form = VetUploadForm()
    file_data = None

    # Handle form submission
    if request.method == 'POST':
        form = VetUploadForm(request.POST, request.FILES)
    if form.is_valid():
        upload = form.save(commit=False)
        upload.user = request.user
        upload.save()
        messages.success(request, 'File uploaded successfully.')
        return redirect('vet:dataset_list')
    else:
        # Show error and re-render page
        messages.error(request, "Please provide all required fields, including a valid file.")
        datasets = DatasetUpload.objects.all().order_by('-uploaded_at')
        uploads = VetUpload.objects.filter(user=request.user).order_by('-uploaded_at')
        return render(request, 'vet/dataset_list.html', {
            'datasets': datasets,
            'uploads': uploads,
            'form': form
        })




    # Load preview for latest upload
    if uploads.exists():
        latest_file = uploads.first().file.path
        try:
            file_data = {}

            if latest_file.endswith('.csv'):
                df = pd.read_csv(latest_file).head(20)
                columns = df.columns.tolist()
                zipped_rows = [zip(columns, row) for row in df.values.tolist()]
                file_data["zipped_rows"] = zipped_rows

            elif latest_file.endswith('.zip'):
                with zipfile.ZipFile(latest_file, 'r') as zip_ref:
                    file_list = zip_ref.namelist()

                    # Optional: filter images only
                    image_files = [f for f in file_list if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

                    # Add to preview (limit to first 20)
                    file_data["zipped_rows"] = list(enumerate(image_files[:20]))

            else:
                messages.warning(request, "Unsupported file type for preview.")
                file_data = None

        except Exception as e:
            messages.warning(request, f"Could not preview uploaded file: {e}")
            file_data = None


        context = {
            'datasets': datasets,
            'uploads': uploads,
            'form': form,
            'file_data': file_data
        }

        return render(request, 'vet/dataset_list.html', context)




@login_required
def delete_upload(request, upload_id):
    try:
        upload = VetUpload.objects.get(id=upload_id, user=request.user)
        file_path = upload.file.path

        # Delete the file from disk
        if os.path.isfile(file_path):
            os.remove(file_path)

        # Delete the model instance
        upload.delete()
        messages.success(request, "File deleted successfully.")
    except VetUpload.DoesNotExist:
        messages.error(request, "File not found or not authorized to delete.")

    return redirect('vet:dataset_list')


@login_required
def vet_report(request):
    if request.user.role not in ['VET', 'FARMER']:
        messages.error(request, "Access denied.")
        return redirect('vet:dashboard')

    # For VET, use assigned_vet; for FARMER, use user
    if request.user.role == 'VET':
        diagnoses = Diagnosis.objects.filter(user=request.user)

    else:
        diagnoses = Diagnosis.objects.filter(user=request.user)

    diagnoses = diagnoses.order_by('-timestamp')

    disease_summary = diagnoses.values('disease_name') \
        .annotate(total=Count('disease_name')) \
        .order_by('-total')

    avg_confidence = diagnoses.aggregate(avg=Avg('confidence'))

    # Handle email form submission
    if request.method == 'POST':
        recipient_email = request.POST.get('recipient_email')
        context = {
            'diagnoses': diagnoses,
            'disease_summary': disease_summary,
            'avg_confidence': round(avg_confidence['avg'] or 0, 1),
            'vet': request.user
        }
        email_html = render_to_string('vet/email_report.html', context)
        email = EmailMessage(
            subject='Vet Report Summary',
            body=email_html,
            from_email='ayanhilwa@gmail.com',
            to=[recipient_email]
        )
        email.content_subtype = 'html'
        email.send()
        messages.success(request, f'Report successfully sent to {recipient_email}')
        return redirect('vet:report')

    context = {
        'diagnoses': diagnoses,
        'disease_summary': disease_summary,
        'avg_confidence': round(avg_confidence['avg'] or 0, 1),
    }
    return render(request, 'vet/report.html', context)


@login_required
def report_view(request):
    user = request.user
    diagnoses = Diagnosis.objects.filter(user=user)


    # Existing stats
    total_diagnoses = diagnoses.count()
    avg_confidence = round(diagnoses.aggregate(Avg('confidence'))['confidence__avg'] or 0, 1)

    # Disease summary
    disease_summary = diagnoses.values('disease_name').annotate(total=Count('id')).order_by('-total')

    context = {
        'diagnoses': diagnoses,
        'avg_confidence': avg_confidence,
        'disease_summary': disease_summary,
        'vet': request.user
    }

    return render(request, 'vet/report.html', context)



# vet/views.py

import pandas as pd

@login_required
def upload_data(request):
    if request.user.role.lower() != 'vet':
        messages.error(request, "Access denied.")
        return redirect('vet:dashboard')

    if request.method == 'POST':
        form = VetUploadForm(request.POST, request.FILES)
        if form.is_valid():
            upload = form.save(commit=False)
            upload.user = request.user
            upload.save()
            messages.success(request, 'File uploaded successfully.')
            return redirect('vet:view_uploads')
    else:
        form = VetUploadForm()

    return render(request, 'vet/dataset_list.html', {'form': form})


# vet/views.py

@login_required
def view_uploads(request):
    if request.user.role.lower() != 'vet':
        messages.error(request, "Access denied.")
        return redirect('vet:dashboard')

    uploads = VetUpload.objects.filter(user=request.user).order_by('-uploaded_at')

    # Read latest uploaded file as DataFrame
    file_data = None
    if uploads.exists():
        latest_file = uploads.first().file.path
        try:
            file_data = pd.read_csv(latest_file).head(20)  # read only top 20 rows
        except Exception as e:
            file_data = None
            messages.warning(request, f"Couldn't parse uploaded file: {e}")

    return render(request, 'vet/view_uploads.html', {
        'uploads': uploads,
        'file_data': file_data,
    })