# **README for Voice-Controlled Smart Retail Store**

This README provides the necessary steps for setting up, running, and testing the **Voice-Controlled Smart Retail Store** application. It outlines all prerequisites, installation instructions, and configurations needed to run the application locally or on a cloud environment.

---

## **Prerequisites**

Before running the application, ensure the following prerequisites are met:

1. **Google Cloud Account:**
   - You'll need a Google Cloud account for deploying cloud services, such as Google Cloud Functions, Google Cloud SQL, Google Kubernetes Engine (GKE), and Google Cloud Storage.

2. **Google Cloud SDK:**
   - Install the **Google Cloud SDK** on your local machine to interact with Google Cloud resources via the command line. [Install Google Cloud SDK](https://cloud.google.com/sdk/docs/install).

3. **Docker:**
   - Ensure **Docker** is installed on your local machine to containerize the app. [Install Docker](https://docs.docker.com/get-docker/).

4. **Python and Django**
   - Install **Python and Django** 

5. **API Keys and Credentials:**
   - Obtain and configure API keys for Google Cloud services:
     - **Google Cloud Speech-to-Text API**
     - **Dialogflow API**
     - **Google Cloud SQL** (for PostgreSQL)
     - **Google Cloud Text-to-Speech API**

6. **Kubernetes Command-line Tool (kubectl):**
   - Install **kubectl** to manage Kubernetes clusters. [Install kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/).

7. **Helm (optional but recommended):**
   - Install **Helm** for managing Kubernetes applications. [Install Helm](https://helm.sh/docs/intro/install/). (redis can be deployed with the help of helm)

---

## **Setup Instructions**

### 1. **Clone the Repository**

Clone the project repository to your local machine:

```bash
git clone https://github.com/your-repo/voice-controlled-smart-retail-store.git
cd voice-controlled-smart-retail-store
cd k8s/
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f ingress.yaml
