# Describes:
Setting up .env
How to push code, build image (if you want locally) or deploy to Cloud Run from repo
Environment variable list
Service account and ADC explanation
Usage of /query endpoint
Explanation of context caching and how system prompt works

## RUN locally
uvicorn main:app --host 0.0.0.0 --port 8000

## Create a private repository
Go to your GitHub profile: https://github.com/DhunganaKB
Click the “+” icon in the upper right and select “New repository”. 
Under Repository name, enter something like gemini_chatbot.
Under Description, you may add: “Gemini Chatbot agent with Vertex AI + Cloud Run”.
Select Private for visibility so only you (and collaborators you add) can see the code. 
(Optionally) Initialize with a README.md, .gitignore (e.g., for Python), and choose license if desired.
Click Create repository.

## Commit code to your repo:
cd gemini_chatbot
git init
git add .
git commit -m "Initial commit: Gemini Chatbot full logic with context caching"
#### Change the URL to your new repo URL:
git remote add origin https://github.com/DhunganaKB/google-gemini-kd1.git
#### Push to GitHub:
git branch -M main
git push -u origin main

## In GCP project long-arcadia-475313-s8, enable APIs:
gcloud services enable aiplatform.googleapis.com run.googleapis.com cloudbuild.googleapis.com --project=long-arcadia-475313-s8

## service account
Create a service account (e.g., chatbot-sa@long-arcadia-475313-s8.iam.gserviceaccount.com) and grant roles: Vertex AI User, Cloud Run Invoker, BigQuery User (if needed).


## Deploy to Cloud Run directly from source:

gcloud run deploy gemini-chatbot-service \
  --region=us-central1 \
  --project=long-arcadia-475313-s8 \
  --source https://github.com/your-org/gemini_chatbot.git \
  --allow-unauthenticated \
  --port=8000 \
  --service-account=chatbot-sa@long-arcadia-475313-s8.iam.gserviceaccount.com \
  --set-env-vars=GOOGLE_CLOUD_PROJECT=long-arcadia-475313-s8,GOOGLE_CLOUD_LOCATION=us-central1,SYSTEM_PROMPT="You are an AI agent specialized in answering SQL queries.",CACHE_TTL_SECONDS=3600

## End point test
Visit your deployed URL and POST to /query endpoint.

## CI/CD 
Set up CI/CD trigger (via Cloud Build) to auto-redeploy on push to main branch.
