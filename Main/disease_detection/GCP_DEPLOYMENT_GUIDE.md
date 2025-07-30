# Google Cloud Platform Deployment Guide for Chicken Health Django App

This guide will walk you through deploying your Django application to Google Cloud Run, using Google Cloud Build for automated deployments, Google Cloud Storage for media and static files, and your existing Supabase database.

## Prerequisites

Before starting, ensure you have:
- A Google Cloud Platform account
- Your Django application ready with all dependencies
- A Supabase database set up
- Your trained model uploaded to Google Drive

## 1. Google Cloud Project Setup

1. **Create a new Google Cloud Project:**
   - Go to the [Google Cloud Console](https://console.cloud.google.com/)
   - Click the project drop-down and select "New Project"
   - Give your project a name (e.g., `chicken-health-app`) and click "Create"

2. **Enable necessary APIs:**
   - In your new project, go to "APIs & Services" > "Library"
   - Search for and enable the following APIs:
     - Cloud Build API
     - Cloud Run Admin API
     - Cloud Storage API
     - Identity and Access Management (IAM) API

3. **Install and initialize the Google Cloud SDK:**
   - Follow the instructions [here](https://cloud.google.com/sdk/docs/install) to install the `gcloud` CLI
   - After installation, run `gcloud init` to authorize the SDK and configure it with your project

## 2. Google Cloud Storage Setup

1. **Create a Cloud Storage Bucket:**
   - In the Cloud Console, go to "Cloud Storage" > "Buckets"
   - Click "Create Bucket"
   - Give your bucket a unique name (e.g., `chicken-health-app-storage`)
   - Choose a location close to your Cloud Run region
   - For "Access control", choose "Fine-grained"
   - Click "Create"

2. **Configure public access:**
   - Go to your newly created bucket's "Permissions" tab
   - Click "Add" and for "New principals", enter `allUsers`
   - For "Role", select "Storage Object Viewer"
   - This makes files in your bucket publicly readable, which is necessary for serving static and media files

3. **Update your bucket name:**
   - Update the `_GS_BUCKET_NAME` variable in your `cloudbuild.yaml` file with your actual bucket name

## 3. Configure Cloud Build

1. **Create a Cloud Build trigger:**
   - In the Cloud Console, go to "Cloud Build" > "Triggers"
   - Click "Create trigger"
   - Give your trigger a name (e.g., `deploy-to-cloud-run`)
   - For "Event", select "Push to a branch"
   - Select your Git repository and branch (e.g., `main` or `master`)
   - For "Configuration", select "Cloud Build configuration file (`cloudbuild.yaml`)"

2. **Environment variables are already configured in the `cloudbuild.yaml` file with your actual values.**

## 4. Deployment Process

1. **Commit and push your changes:**
   ```bash
   git add .
   git commit -m "Deploy to Google Cloud Run"
   git push origin main
   ```

2. **Monitor the build:**
   - Go to "Cloud Build" > "History" in the Cloud Console
   - You should see a new build in progress
   - Click on it to see the logs and monitor progress

3. **Access your application:**
   - Once the build is complete, go to the "Cloud Run" page
   - You will see your deployed service
   - Click on it to see the URL where your application is running

## 5. Post-Deployment Steps

1. **Test your application:**
   - Visit the provided URL
   - Test image upload and prediction functionality
   - Verify database connectivity

2. **Set up custom domain (optional):**
   - In Cloud Run, go to "Manage Custom Domains"
   - Add your domain and follow the verification steps

3. **Configure monitoring:**
   - Set up Cloud Monitoring for your application
   - Configure alerts for errors or performance issues

## 6. Troubleshooting

**Common issues and solutions:**

- **Build fails:** Check the Cloud Build logs for specific error messages
- **Database connection issues:** Verify your Supabase credentials in the substitution variables
- **Static files not loading:** Ensure your GCS bucket has proper permissions
- **Model loading errors:** Verify the Google Drive model ID is correct and the file is publicly accessible

## 7. Security Considerations

- **Never commit sensitive credentials to version control**
- **Use Cloud Build substitution variables for secrets**
- **Regularly rotate your database passwords**
- **Monitor your application for security vulnerabilities**
- **Enable Cloud Armor for DDoS protection if needed**

## 8. File Structure Summary

Your deployment includes these key files:
- `cloudbuild.yaml` - Cloud Build configuration with environment variables
- `Dockerfile` - Container configuration
- `requirements.txt` - Python dependencies
- `settings.py` - Django configuration for production
- `.dockerignore` - Files to exclude from Docker build

## Credentials and Security
- Service Account: kukuintel@kukuintel.iam.gserviceaccount.com
- All sensitive credentials are managed through Cloud Build substitution variables