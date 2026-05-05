# Integrated Manufacturing AI Platform

A prototype system that combines **Generative AI**, **Agent-based workflows**, and **containerized deployment** to simulate a manufacturing planning pipeline.

---

## Overview

This project demonstrates how AI can support early-stage manufacturing decisions.
It allows users to generate:

* A **manufacturing concept narrative + visual** (GenAI)
* A **structured strategy report** using a simple **Researcher → Writer agent workflow**

The system is deployed using **Docker and Kubernetes**, showing how AI services can be packaged and scaled.

---

## Core Components

* **Flask API** – backend service for AI pipelines
* **Streamlit UI** – interactive frontend for user input
* **GenAI Module** – generates text + image outputs
* **Agent System** – two-step workflow (research → report generation)
* **Vector Store** – simple retrieval from local knowledge base

---

## How It Works

1. User inputs a manufacturing idea or objective
2. System processes it in two ways:

   * **GenAI pipeline** → concept description + image
   * **Agent pipeline** → structured manufacturing report
3. Results are displayed in a web interface

---

## Tech Stack

* Python (Flask, Streamlit)
* LangChain / CrewAI (agent workflow) 
* Docker & Docker Compose
* Kubernetes (Minikube deployment)

---

## Running the Project

### Local (without Docker)

```bash
pip install -r requirements.txt
python -m app.main
```

```bash
streamlit run frontend/streamlit_app.py
```

---

### Docker

```bash
docker compose up --build
```

---

### Kubernetes (Minikube)

```bash
minikube start
kubectl apply -f k8s/
```

---

## Notes

* The system runs in **mock mode by default**, so it works without API keys
* LLM/image APIs can be enabled via `.env`
* Retrieval is keyword-based (not embedding-based yet)

---

## Limitations

* Agent workflow is sequential, not fully autonomous
* Retrieval system is basic (no semantic search)
* Output quality depends on external APIs

---

## Author

Aaditi Bhale
