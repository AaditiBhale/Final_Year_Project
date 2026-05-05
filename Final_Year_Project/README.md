# Integrated Manufacturing AI Platform

Single platform that combines:
- **Docker + Kubernetes deployment** of a Python Flask manufacturing app
- **Multimodal GenAI** (text narrative + generated image)
- **Agentic AI** (Researcher Agent -> Writer Agent workflow)
- **Soothing Streamlit frontend** for user interaction

## 1) Architecture

- `app/main.py`: Flask API service
- `app/services/genai.py`: multimodal GenAI pipeline (LLM + image model API)
- `app/services/agents.py`: multi-agent workflow with hand-off
- `app/services/vector_store.py`: local retrieval layer (starter vector DB replacement)
- `frontend/streamlit_app.py`: user-friendly UI
- `docker-compose.yml`: local multi-container runtime
- `k8s/*.yaml`: Minikube-ready deployment with rolling updates

## 2) Prerequisites

- Python 3.11+
- Docker Desktop
- kubectl
- Minikube

## 3) Local Run (No Docker)

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python -m app.main
```

Open new terminal:

```bash
streamlit run frontend/streamlit_app.py
```

- Flask API: `http://localhost:5000`
- Streamlit UI: `http://localhost:8501`

## 4) Local Run (Docker Desktop + Compose)

```bash
copy .env.example .env
docker compose up --build
```

- Streamlit UI: `http://localhost:8502`
- Backend health: `http://localhost:5001/health`

Stop:

```bash
docker compose down
```

## 5) Kubernetes on Minikube (Docker Objective)

### A. Start Minikube
```bash
minikube start --driver=docker
```

### B. Build images into Minikube Docker daemon
```bash
minikube docker-env | Invoke-Expression
docker build -t mfg-backend:v1 .
docker build -t mfg-frontend:v1 -f frontend/Dockerfile .
```

### C. Apply manifests
```bash
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl get pods
kubectl get svc
```

### D. Access frontend
```bash
minikube service mfg-frontend-svc --url
```

## 6) Rolling Update Demo (Zero Downtime)

1. Make change in code.
2. Rebuild backend image with new tag:
```bash
docker build -t mfg-backend:v2 .
```
3. Update deployment image:
```bash
kubectl set image deployment/mfg-backend mfg-backend=mfg-backend:v2
kubectl rollout status deployment/mfg-backend
kubectl get pods -w
```

Because `maxUnavailable: 0` and readiness probes are configured, rollout maintains availability.

## 7) Real API Keys (Optional)

Set `.env` values:
- `LLM_API_KEY`
- `IMAGE_API_KEY`
- `USE_MOCK_MODE=false`

Default mode is mock (`USE_MOCK_MODE=true`) so the platform works immediately without paid APIs.

## 8) CI/CD Starter

GitHub Actions pipeline in `.github/workflows/ci.yml`:
- Installs dependencies
- Performs app smoke test
- Builds backend/frontend Docker images

You can later extend it to push images and deploy to cluster.
