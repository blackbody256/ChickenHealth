# Google Cloud Platform Deployment Guide for Chicken Health Django App

This guide will walk you through deploying your Django application to Google Cloud Run, using Google Cloud Build for automated deployments, Google Cloud Storage for media and static files, and your existing Supabase database.

## 1. Google Cloud Project Setup

1.  **Create a new Google Cloud Project:**
    *   Go to the [Google Cloud Console](https://console.cloud.google.com/).
    *   Click the project drop-down and select "New Project".
    *   Give your project a name (e.g., `chicken-health-app`) and click "Create".

2.  **Enable necessary APIs:**
    *   In your new project, go to the "APIs & Services" > "Library".
    *   Search for and enable the following APIs:
        *   Cloud Build API
        *   Cloud Run Admin API
        *   Cloud Storage API
        *   Identity and Access Management (IAM) API

3.  **Install and initialize the Google Cloud SDK:**
    *   Follow the instructions [here](https://cloud.google.com/sdk/docs/install) to install the `gcloud` CLI.
    *   After installation, run `gcloud init` to authorize the SDK and configure it with your project.

## 2. Google Cloud Storage Setup

1.  **Create a Cloud Storage Bucket:**
    *   In the Cloud Console, go to "Cloud Storage" > "Buckets".
    *   Click "Create Bucket".
    *   Give your bucket a unique name (e.g., `chicken-health-app-storage`).
    *   Choose a location and storage class (Standard is fine).
    *   For "Access control", choose "Fine-grained".
    *   Click "Create".

2.  **Configure public access:**
    *   Go to your newly created bucket's "Permissions" tab.
    *   Click "Add" and for "New principals", enter `allUsers`.
    *   For "Role", select "Storage Object Viewer".
    *   This makes files in your bucket publicly readable, which is necessary for serving static and media files.

## 3. Configure Environment Variables in Cloud Build

We will use substitutions in our `cloudbuild.yaml` file to manage secret environment variables. This is more secure than hardcoding them.

1.  **Go to Cloud Build Triggers:**
    *   In the Cloud Console, go to "Cloud Build" > "Triggers".
    *   Click "Create trigger".
    *   Give your trigger a name (e.g., `deploy-to-cloud-run`).
    *   For "Event", select "Push to a branch".
    *   Select your Git repository and branch (e.g., `main` or `master`).
    *   For "Configuration", select "Cloud Build configuration file (`cloudbuild.yaml`)".
    *   Under "Advanced" > "Substitution variables", add the following:
        *   `_MODEL_GDRIVE_ID`: Your Google Drive model ID.
        *   `_GS_BUCKET_NAME`: The name of your Cloud Storage bucket.
        *   `_DATABASE_URL`: Your Supabase database connection string.
        *   `_SECRET_KEY`: Your Django `SECRET_KEY`.

## 4. Deployment

With everything configured, you are ready to deploy.

1.  **Commit and push your changes:**
    *   Commit all the changes we've made to your Git repository.
    *   Push the changes to the branch you configured in your Cloud Build trigger.

2.  **Monitor the build:**
    *   Go to the "Cloud Build" > "History" page in the Cloud Console.
    *   You should see a new build in progress. You can click on it to see the logs.

3.  **Access your application:**
    *   Once the build is complete, go to the "Cloud Run" page.
    *   You will see your deployed service. Click on it to see the URL where your application is running.

## 5. File Modifications Summary

Here is a summary of the changes we made to your files:

*   **`requirements.txt`:**
    *   Added `gdown` to download your model from Google Drive.
    *   Added `django-storages[google]` to handle static and media files with Google Cloud Storage.

*   **`Dockerfile`:**
    *   Added a build argument for the Google Drive model ID.
    *   Used `gdown` to download the model during the build process.
    *   Updated the `CMD` to run the application with Gunicorn.

*   **`disease_detection/settings.py`:**
    *   Configured `django-storages` to use Google Cloud Storage for static and media files in production.
    *   Removed the hardcoded production settings.

*   **`cloudbuild.yaml` (New File):**
    *   Defines the steps for Cloud Build to build your Docker image and deploy it to Cloud Run.

*   **`GCP_DEPLOYMENT_GUIDE.md` (This File):**
    *   Provides step-by-step instructions for deploying your application to Google Cloud.




## Credentials and security
- kukuintel@kukuintel.iam.gserviceaccount.com