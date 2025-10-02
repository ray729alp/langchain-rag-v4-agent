# Agency Chatbot - Vertex AI Integration

A comprehensive chatbot solution for an government agency (Malaysian Qualifications Agency) built with Flask and Google Cloud's Vertex AI (Dialogflow CX). This intelligent chatbot handles inquiries about informations regrading/related to the agency and their services with advanced AI capabilities.

## 📋 Table of Contents

- [Architecture Overview](#-architecture-overview)
- [Prerequisites](#-prerequisites)
- [Complete Setup Guide](#-complete-setup-guide)
  - [Step 1: Google Cloud Platform Account Setup](#step-1-google-cloud-platform-account-setup)
  - [Step 2: GCP Project Creation](#step-2-gcp-project-creation)
  - [Step 3: Billing Account Setup](#step-3-billing-account-setup)
  - [Step 4: Enable Required APIs](#step-4-enable-required-apis)
  - [Step 5: Service Account Creation](#step-5-service-account-creation)
  - [Step 6: Vertex AI Agent Setup](#step-6-vertex-ai-agent-setup)
  - [Step 7: Cloud Storage Setup](#step-7-cloud-storage-setup)
  - [Step 8: Local Development Setup](#step-8-local-development-setup)
  - [Step 9: Application Configuration](#step-9-application-configuration)
  - [Step 10: Testing](#step-10-testing)
  - [Step 11: Production Deployment](#step-11-production-deployment)
- [Troubleshooting](#-troubleshooting)
- [Monitoring & Maintenance](#-monitoring--maintenance)
- [Security Considerations](#-security-considerations)
- [Support](#-support)

## 🏗️ Architecture Overview

```
Frontend (HTML/CSS/JS) 
        ↓
Flask Backend (Python)
        ↓
Vertex AI Agent (Dialogflow CX)
        ↓
Knowledge Base (MQA Documents)
        ↓
Cloud Storage (Document Storage)
```

**Technology Stack:**
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Backend**: Python Flask
- **AI/ML**: Google Vertex AI (Dialogflow CX)
- **Storage**: Google Cloud Storage
- **Authentication**: Google Service Accounts
- **Deployment**: Google Cloud Run / App Engine

## 🎯 Prerequisites

### Software Requirements
- **Python 3.8+** ([Download](https://www.python.org/downloads/))
- **Git** ([Download](https://git-scm.com/downloads))
- **Google Cloud SDK** ([Download](https://cloud.google.com/sdk/docs/install))
- **Web Browser** (Chrome, Firefox, Safari, or Edge)

### Account Requirements
- **Google Account** (Gmail account)
- **Google Cloud Platform Account** (Free tier available with $300 credit)

### Knowledge Requirements
- Basic command line usage
- Basic understanding of web applications
- Familiarity with Google Cloud Platform (helpful but not required)

## 🚀 Complete Setup Guide

### Step 1: Google Cloud Platform Account Setup

#### 1.1 Create Google Account (if needed)
1. Go to [accounts.google.com](https://accounts.google.com)
2. Click "Create account"
3. Follow the steps to create a new Google account
4. Verify your email address and phone number

#### 1.2 Sign Up for Google Cloud Platform
1. Navigate to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Get started for free"
3. Sign in with your Google account
4. Accept the terms of service
5. Provide billing information (requires credit card, but free tier includes $300 credit)

### Step 2: GCP Project Creation

#### 2.1 Create New Project
1. In Google Cloud Console, click the project dropdown in top navigation
2. Click "New Project"
3. Fill in project details:
   - **Project Name**: `mqa-chatbot-production`
   - **Project ID**: `mqa-chatbot-{unique-id}` (auto-generated, you can customize)
   - **Location**: No organization (if personal account)
4. Click "Create"
5. Wait for project creation (usually 1-2 minutes)

#### 2.2 Set Project as Active
1. Click the project dropdown in top navigation
2. Select your newly created project `mqa-chatbot-production`

### Step 3: Billing Account Setup

#### 3.1 Link Billing Account
1. Navigation Menu → Billing
2. Click "Manage Billing Accounts"
3. Click "Create Account" (if no existing billing account)
4. Fill in billing information:
   - Account name: `MQA-Chatbot-Billing`
   - Country: Malaysia
   - Currency: MYR
   - Add payment method (credit card)
5. Link billing account to your project

#### 3.2 Set Budget Alerts (Recommended)
1. Navigation Menu → Billing → Budgets & alerts
2. Click "Create budget"
3. Configure:
   - Budget name: `MQA-Chatbot-Monthly-Budget`
   - Amount: Set reasonable limit (e.g., $50/month)
   - Alert threshold: 50%, 90%, 100%
4. Click "Create"

### Step 4: Enable Required APIs

#### 4.1 Enable APIs via Console
1. Navigation Menu → APIs & Services → Library
2. Search for and enable each API:

**Required APIs:**
- **Dialogflow API**
- **Cloud Storage JSON API**
- **IAM Service Account Credentials API**
- **Cloud Logging API**
- **Cloud Monitoring API**

**Enable each API:**
1. Search for the API name
2. Click on the API from results
3. Click "Enable"
4. Wait for enabling to complete

#### 4.2 Verify Enabled APIs
1. Navigation Menu → APIs & Services → Dashboard
2. Confirm all required APIs show "Enabled" status

### Step 5: Service Account Creation

#### 5.1 Create Service Account
1. Navigation Menu → IAM & Admin → Service Accounts
2. Click "Create Service Account"
3. Fill in details:
   - **Service account name**: `mqa-chatbot-agent`
   - **Service account ID**: `mqa-chatbot-agent` (auto-filled)
   - **Description**: "Service account for MQA Chatbot Vertex AI integration"
4. Click "Create and Continue"

#### 5.2 Assign Required Roles
Add these roles to the service account:
- **Dialogflow API Client**
- **Storage Object Viewer**
- **Vertex AI User**
- **Logs Writer** (for logging)
- **Monitoring Metric Writer** (for monitoring)

**Steps:**
1. In "Grant access" section, add each role:
   - Click "Add another role"
   - Select role from dropdown
   - Repeat for all required roles
2. Click "Continue"
3. Click "Done"

#### 5.3 Generate Service Account Key
1. Click on the created service account (`mqa-chatbot-agent`)
2. Go to "Keys" tab
3. Click "Add Key" → "Create new key"
4. Select "JSON" format
5. Click "Create"
6. The key file will download automatically
7. **Important**: Save this file securely as `mqa-chatbot-credentials.json`

### Step 6: Vertex AI Agent Setup

#### 6.1 Create Dialogflow CX Agent
1. Navigation Menu → Vertex AI → Dialogflow CX
2. Click "Create Agent"
3. Fill in agent details:
   - **Display name**: `MQA-Chatbot-Agent`
   - **Default language**: English
   - **Location**: `us-central1` (recommended for better performance)
   - **Time zone**: `(UTC+08:00) Kuala Lumpur, Singapore`
   - **Google Cloud Project**: Your project (`mqa-chatbot-production`)
4. Click "Create"

#### 6.2 Get Agent ID
1. After agent creation, you'll be redirected to the agent console
2. Copy the Agent ID from the URL:
   ```
   https://dialogflow.cloud.google.com/cx/projects/{project-id}/locations/{location}/agents/{agent-id}
   ```
   The `{agent-id}` is what you need
3. Save this Agent ID for later use

#### 6.3 Configure Knowledge Base
1. In Dialogflow CX console, go to "Manage" tab → "Knowledge"
2. Click "Create"
3. Fill in knowledge base details:
   - **Display name**: `MQA-Knowledge-Base`
   - **Knowledge types**: Select all applicable types
4. Click "Create"

#### 6.4 Add Documents to Knowledge Base
1. Click on your knowledge base
2. Click "Create" to add documents
3. Upload MQA documents:
   - Accreditation guidelines (PDF)
   - Qualification frameworks (PDF)
   - APEL documentation (PDF)
   - FAQ documents (PDF/TXT)
4. For each document:
   - **Display name**: Descriptive name (e.g., "MQA Accreditation Guidelines")
   - **MIME type**: Select appropriate type (PDF, TXT, etc.)
   - **Upload file**: Choose file from your computer
5. Click "Create" for each document

### Step 7: Cloud Storage Setup

#### 7.1 Create Storage Bucket
1. Navigation Menu → Cloud Storage → Buckets
2. Click "Create"
3. Configure bucket:
   - **Name**: `mqa-chatbot-documents-{unique-id}` (must be globally unique)
   - **Location type**: Region
   - **Location**: `us-central1` (same as your agent)
   - **Storage class**: Standard
   - **Access control**: Uniform
4. Click "Create"

#### 7.2 Upload Additional Documents
1. Click on your created bucket
2. Click "Upload files"
3. Select all MQA-related documents
4. Organize in folders if needed:
   - `accreditation/`
   - `qualifications/`
   - `apel/`
   - `frameworks/`

#### 7.3 Configure Bucket Permissions
1. In bucket details, go to "Permissions" tab
2. Click "Grant access"
3. Add principal: `mqa-chatbot-agent@your-project-id.iam.gserviceaccount.com`
4. Assign role: `Storage Object Viewer`
5. Click "Save"

### Step 8: Local Development Setup

#### 8.1 Clone Repository
```bash
# Clone the project repository
git clone https://github.com/your-username/mqa-chatbot.git
cd mqa-chatbot
```

#### 8.2 Set Up Python Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 8.3 Install Google Cloud SDK (if not installed)
```bash
# Download and install Google Cloud SDK
# Follow instructions at: https://cloud.google.com/sdk/docs/install

# Initialize gcloud (if using local authentication)
gcloud init

# Authenticate with your account
gcloud auth login
```

### Step 9: Application Configuration

#### 9.1 Project Structure Setup
```bash
# Create necessary directories
mkdir -p credentials static/images templates logs

# Verify project structure
mqa-chatbot/
├── app.py
├── chat.py
├── requirements.txt
├── .env
├── .gitignore
├── credentials/
│   └── mqa-chatbot-credentials.json
├── static/
│   ├── style.css
│   ├── app.js
│   └── images/
│       ├── mqa-logo.png
│       ├── accreditation.png
│       ├── framework.png
│       ├── qualifications.png
│       ├── recognition.png
│       ├── equivalency.png
│       ├── apel.png
│       └── faq.png
├── templates/
│   └── base.html
└── logs/
    └── app.log
```

#### 9.2 Place Credentials File
1. Move your downloaded `mqa-chatbot-credentials.json` to `credentials/` folder
2. Verify the path: `credentials/mqa-chatbot-credentials.json`

#### 9.3 Environment Configuration
Create `.env` file in project root:

```env
# Flask Configuration
FLASK_SECRET_KEY=your-super-secret-key-change-in-production-2024
FLASK_DEBUG=False
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# Google Cloud Configuration
GOOGLE_APPLICATION_CREDENTIALS=credentials/mqa-chatbot-credentials.json
GCP_PROJECT_ID=your-actual-project-id-here
AGENT_ID=your-actual-agent-id-here
AGENT_LOCATION=us-central1
LANGUAGE_CODE=en

# Application Settings
CHATBOT_NAME=MQA Assistant
CHATBOT_DESCRIPTION=Malaysian Qualifications Agency Chatbot
```

**How to find your values:**
- `GCP_PROJECT_ID`: Navigation Menu → IAM & Admin → Settings
- `AGENT_ID`: Dialogflow CX agent URL (the long string after /agents/)
- `AGENT_LOCATION`: Region you selected (us-central1, asia-southeast1, etc.)

#### 9.4 Add Category Images
Place the following images in `static/images/` directory:
- `mqa-logo.png` (Main logo, 40x40px recommended)
- `accreditation.png` (Accreditation category icon)
- `framework.png` (Framework category icon)
- `qualifications.png` (Qualifications category icon)
- `recognition.png` (Recognition category icon)
- `equivalency.png` (Equivalency category icon)
- `apel.png` (APEL category icon)
- `faq.png` (FAQ category icon)

### Step 10: Testing

#### 10.1 Local Development Test
```bash
# Set environment variable (optional, if not in .env)
export GOOGLE_APPLICATION_CREDENTIALS="credentials/mqa-chatbot-credentials.json"

# Run the application
python app.py
```

#### 10.2 Verify Application Running
1. Open web browser
2. Navigate to: `http://localhost:5000`
3. You should see the MQA chat interface

#### 10.3 Test Health Endpoint
```bash
# Test API health
curl http://localhost:5000/health

# Expected response:
{
  "status": "healthy",
  "vertex_ai_initialized": true,
  "project_id": "your-project-id",
  "agent_id": "your-agent-id"
}
```

#### 10.4 Comprehensive Chatbot Testing
Test each category thoroughly:

1. **Accreditation Process & Status**
   - Ask about timeline
   - Document requirements
   - Status checking

2. **MQA Framework**
   - MQF levels
   - Policy documents
   - Framework standards

3. **APEL Categories**
   - APEL.A (Access)
   - APEL.C (Credit Transfer)
   - APEL.Q (Qualifications)
   - APEL.M (Micro-credentials)

4. **Other Categories**
   - Qualification Standards
   - Recognition of Qualification
   - Equivalency of Qualification
   - Frequently Asked Questions

#### 10.5 API Testing
```bash
# Test chatbot API directly
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the accreditation process?"}'
```

### Step 11: Production Deployment

#### 11.1 Prepare for Deployment

**Update .env for production:**
```env
FLASK_SECRET_KEY=generate-a-secure-random-key-for-production
FLASK_DEBUG=False
FLASK_HOST=0.0.0.0
FLASK_PORT=8080
```

**Create requirements.txt:**
```txt
flask==2.3.3
google-cloud-dialogflow-cx==1.15.0
google-auth==2.22.0
python-dotenv==1.0.0
flask-limiter==3.3.0
gunicorn==21.2.0
```

#### 11.2 Deployment Option 1: Google Cloud Run (Recommended)

**Create Dockerfile:**
```dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -r appuser && chown -R appuser /app
USER appuser

# Expose port
EXPOSE 8080

# Start application
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
```

**Create .dockerignore:**
```gitignore
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env
venv
.venv
credentials/*.json
.git
.github
Dockerfile
.dockerignore
```

**Deploy to Cloud Run:**
```bash
# Build and deploy
gcloud run deploy mqa-chatbot \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1

# Set environment variables in Cloud Run
gcloud run services update mqa-chatbot \
  --update-env-vars \
FLASK_SECRET_KEY=your-production-secret-key,\
GCP_PROJECT_ID=your-project-id,\
AGENT_ID=your-agent-id,\
AGENT_LOCATION=us-central1,\
LANGUAGE_CODE=en
```

#### 11.3 Deployment Option 2: Google App Engine

**Create app.yaml:**
```yaml
runtime: python39
entrypoint: gunicorn -b :$PORT app:app

env_variables:
  FLASK_SECRET_KEY: "your-production-secret-key"
  GCP_PROJECT_ID: "your-project-id"
  AGENT_ID: "your-agent-id"
  AGENT_LOCATION: "us-central1"
  LANGUAGE_CODE: "en"

handlers:
- url: /static
  static_dir: static

- url: /.*
  script: auto

instance_class: F2
```

**Deploy to App Engine:**
```bash
gcloud app deploy
```

#### 11.4 Deployment Option 3: Traditional VPS/Server

**Setup production server:**
```bash
# Install dependencies
sudo apt update
sudo apt install python3-pip python3-venv nginx

# Create production directory
sudo mkdir -p /var/www/mqa-chatbot
sudo chown $USER:$USER /var/www/mqa-chatbot

# Copy application files
cp -r . /var/www/mqa-chatbot/

# Setup virtual environment
cd /var/www/mqa-chatbot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt gunicorn

# Create systemd service
sudo nano /etc/systemd/system/mqa-chatbot.service
```

**mqa-chatbot.service:**
```ini
[Unit]
Description=MQA Chatbot Gunicorn Service
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/mqa-chatbot
Environment="PATH=/var/www/mqa-chatbot/venv/bin"
ExecStart=/var/www/mqa-chatbot/venv/bin/gunicorn --workers 3 --bind unix:mqa-chatbot.sock -m 007 app:app

[Install]
WantedBy=multi-user.target
```

**Nginx configuration:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/mqa-chatbot/mqa-chatbot.sock;
    }

    location /static {
        alias /var/www/mqa-chatbot/static;
    }
}
```

## 🛠️ Troubleshooting

### Common Issues and Solutions

#### 1. Credentials Issues
```bash
# Error: Could not automatically determine credentials
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/credentials/mqa-chatbot-credentials.json"

# Verify credentials work
gcloud auth activate-service-account --key-file=credentials/mqa-chatbot-credentials.json
```

#### 2. Dialogflow Agent Access Issues
- Verify Agent ID is correct
- Check service account has Dialogflow API Client role
- Confirm agent location matches environment variable

#### 3. Import Errors
```bash
# Reinstall dependencies
pip uninstall -r requirements.txt -y
pip install -r requirements.txt

# Check Python version
python --version  # Should be 3.8+
```

#### 4. Port Already in Use
```bash
# Find and kill process using port 5000
lsof -ti:5000 | xargs kill -9

# Or use different port
FLASK_PORT=5001 python app.py
```

#### 5. Memory Issues in Production
- Increase Cloud Run memory to 2Gi
- Add more workers in gunicorn configuration
- Implement request timeouts

### Debug Mode
Enable debug mode for development:
```env
FLASK_DEBUG=True
```

Check logs in `logs/app.log` for detailed error information.

## 📊 Monitoring & Maintenance

### 1. Google Cloud Monitoring Setup

**Create Monitoring Dashboard:**
1. Navigation Menu → Monitoring → Dashboards
2. Create custom dashboard for:
   - API request counts
   - Error rates
   - Response latency
   - Resource usage

**Set Up Alerts:**
1. Navigation Menu → Monitoring → Alerting
2. Create policy for:
   - High error rates (>5%)
   - High latency (>10s)
   - Budget alerts

### 2. Regular Maintenance Tasks

**Weekly:**
- Check application logs for errors
- Monitor API usage and quotas
- Verify knowledge base documents are accessible

**Monthly:**
- Update Python dependencies
- Review and rotate service account keys if needed
- Check GCP billing and usage

**Quarterly:**
- Update knowledge base with new MQA documents
- Review and update chatbot responses
- Performance testing and optimization

### 3. Backup Strategy

**Application Backup:**
```bash
# Backup application code
tar -czf mqa-chatbot-backup-$(date +%Y%m%d).tar.gz /var/www/mqa-chatbot

# Backup credentials (securely)
gcloud kms encrypt --plaintext-file=credentials.json --ciphertext-file=credentials.json.enc
```

**GCP Resources Backup:**
- Enable Object Versioning in Cloud Storage
- Export Dialogflow agent regularly
- Backup Cloud SQL databases (if used)

## 🔒 Security Considerations

### 1. Credential Security
- Never commit credential files to version control
- Use environment variables in production
- Regularly rotate service account keys
- Store credentials in secure secret management systems

### 2. Application Security
```python
# In app.py - Security headers
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response
```

### 3. GCP Security Best Practices
- Follow principle of least privilege for IAM roles
- Enable Cloud Audit Logs
- Use VPC Service Controls if needed
- Implement DDoS protection

### 4. Data Privacy
- Ensure no PII (Personally Identifiable Information) in logs
- Implement data retention policies
- Regular security assessments

## 📞 Support

### Getting Help

**Application Issues:**
1. Check application logs: `logs/app.log`
2. Verify environment variables are set correctly
3. Test health endpoint: `/health`

**GCP Issues:**
1. Check Google Cloud Status Dashboard
2. Review GCP project quotas and limits
3. Verify API enablement and permissions

**Vertex AI/Dialogflow Issues:**
1. Check Dialogflow CX agent training status
2. Verify knowledge base document processing
3. Test agent in Dialogflow CX console

### Emergency Contacts
- **GCP Support**: https://cloud.google.com/support
- **Dialogflow Documentation**: https://cloud.google.com/dialogflow/docs

### Documentation Resources
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Dialogflow CX Documentation](https://cloud.google.com/dialogflow/cx/docs)
- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)

---

## 🎉 Success Checklist

- [ ] GCP Project created and billing set up
- [ ] Required APIs enabled
- [ ] Service account created with proper roles
- [ ] Dialogflow CX agent configured
- [ ] Knowledge base populated with MQA documents
- [ ] Cloud Storage bucket created
- [ ] Local development environment working
- [ ] All environment variables configured
- [ ] Application tested locally
- [ ] Production deployment completed
- [ ] Monitoring and alerts configured
- [ ] Security measures implemented

**Congratulations!** The Agency Chatbot is now ready to serve users with intelligent responses about MQA services and qualifications.

---

*Last Updated: 2 October 2025*  
*Maintained by: Ray Clement*  
*Version: 1.0.0*
