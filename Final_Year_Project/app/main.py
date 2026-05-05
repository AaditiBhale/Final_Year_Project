from __future__ import annotations

from flask import Flask, jsonify, request
from dotenv import load_dotenv

from app.services.agents import AgenticManufacturingSystem
from app.services.genai import MultimodalGenerator
from app.services.vector_store import ManufacturingVectorStore

load_dotenv()
app = Flask(__name__)

retriever = ManufacturingVectorStore()
genai_pipeline = MultimodalGenerator(retriever)
agent_system = AgenticManufacturingSystem(retriever)


@app.get("/health")
def health() -> tuple:
    return jsonify({"status": "ok", "service": "manufacturing-platform"}), 200


@app.post("/api/genai/create")
def create_multimodal() -> tuple:
    payload = request.get_json(silent=True) or {}
    prompt = payload.get("prompt", "").strip()
    if not prompt:
        return jsonify({"error": "prompt is required"}), 400
    try:
        result = genai_pipeline.generate(prompt)
        return jsonify(result), 200
    except Exception as exc:
        return jsonify({"error": "genai_generation_failed", "details": str(exc)}), 500


@app.post("/api/agentic/run")
def run_agentic() -> tuple:
    payload = request.get_json(silent=True) or {}
    topic = payload.get("topic", "").strip()
    if not topic:
        return jsonify({"error": "topic is required"}), 400
    try:
        result = agent_system.run(topic)
        return jsonify(result), 200
    except Exception as exc:
        return jsonify({"error": "agentic_pipeline_failed", "details": str(exc)}), 500


@app.get("/")
def index() -> tuple:
    return (
        jsonify(
            {
                "name": "Integrated Manufacturing Platform",
                "features": [
                    "Multimodal GenAI concept creator",
                    "Agentic Researcher + Writer workflow",
                    "Docker + Kubernetes deployment ready",
                ],
            }
        ),
        200,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
