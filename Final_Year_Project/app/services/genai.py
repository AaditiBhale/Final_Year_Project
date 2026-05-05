from __future__ import annotations

import base64
import os
from dataclasses import dataclass
from typing import Dict, List

import requests

from app.services.vector_store import ManufacturingVectorStore


@dataclass
class GenAIConfig:
    llm_api_key: str
    llm_api_base: str
    llm_model: str
    image_api_key: str
    image_api_base: str
    use_mock_mode: bool


class MultimodalGenerator:
    def __init__(self, retriever: ManufacturingVectorStore) -> None:
        self.retriever = retriever
        self.cfg = GenAIConfig(
            llm_api_key=os.getenv("LLM_API_KEY", ""),
            llm_api_base=os.getenv("LLM_API_BASE", "https://api.openai.com/v1"),
            llm_model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            image_api_key=os.getenv("IMAGE_API_KEY", ""),
            image_api_base=os.getenv(
                "IMAGE_API_BASE", "https://api.openai.com/v1/images/generations"
            ),
            use_mock_mode=os.getenv("USE_MOCK_MODE", "true").lower() == "true",
        )

    def generate(self, prompt: str) -> Dict[str, object]:
        context = self.retriever.retrieve(prompt, top_k=3)
        narrative = self._generate_text(prompt, context)
        image_url = self._generate_image(prompt)
        return {
            "prompt": prompt,
            "retrieved_context": context,
            "narrative": narrative,
            "image_url": image_url,
        }

    def _generate_text(self, prompt: str, context: List[str]) -> str:
        if self.cfg.use_mock_mode or not self._is_real_token(self.cfg.llm_api_key):
            return (
                f"Manufacturing concept brief for '{prompt}':\n"
                "- Product vision: Modular and scalable.\n"
                "- Material strategy: Sustainable alloy + recyclable polymers.\n"
                "- Process: CAD -> Rapid prototyping -> Pilot assembly.\n"
                f"- Context highlights: {context[:2]}"
            )

        payload = {
            "model": self.cfg.llm_model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a manufacturing domain assistant. "
                        "Create concise, practical product concept writeups."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Prompt: {prompt}\nContext: {context}",
                },
            ],
            "temperature": 0.4,
            "max_tokens": 700,
        }
        headers = {
            "Authorization": f"Bearer {self.cfg.llm_api_key}",
            "Content-Type": "application/json",
        }
        if "openrouter.ai" in self.cfg.llm_api_base:
            headers["HTTP-Referer"] = "http://localhost"
            headers["X-Title"] = "Integrated Manufacturing AI Platform"
        try:
            response = requests.post(
                f"{self.cfg.llm_api_base}/chat/completions",
                json=payload,
                headers=headers,
                timeout=45,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception:
            # Keep the demo responsive even if upstream API is unavailable.
            return (
                f"Manufacturing concept brief for '{prompt}':\n"
                "- Product vision: Modular and scalable.\n"
                "- Material strategy: Sustainable alloy + recyclable polymers.\n"
                "- Process: CAD -> Rapid prototyping -> Pilot assembly.\n"
                f"- Context highlights: {context[:2]}"
            )

    def _generate_image(self, prompt: str) -> str:
        if self.cfg.use_mock_mode or not self._is_real_token(self.cfg.image_api_key):
            safe_prompt = requests.utils.quote(prompt)
            return f"https://image.pollinations.ai/prompt/{safe_prompt}"

        if not self.cfg.image_api_base.startswith("http"):
            return (
                "https://placehold.co/1024x1024/png?"
                "text=Manufacturing+Prototype+Concept"
            )

        image_prompt = (
            f"High-fidelity industrial product prototype render: {prompt}. "
            "Studio lighting, engineering context, photoreal style."
        )
        headers = {
            "Authorization": f"Bearer {self.cfg.image_api_key}",
            "Content-Type": "application/json",
        }
        if "huggingface.co" in self.cfg.image_api_base:
            hf_endpoint = self._resolve_hf_image_endpoint(self.cfg.image_api_base)
            try:
                response = requests.post(
                    hf_endpoint,
                    json={"inputs": image_prompt, "options": {"wait_for_model": True}},
                    headers=headers,
                    timeout=120,
                )
                response.raise_for_status()
                content_type = response.headers.get("content-type", "")
                if "image" in content_type:
                    encoded = base64.b64encode(response.content).decode("utf-8")
                    return f"data:{content_type};base64,{encoded}"
                data = response.json()
                if isinstance(data, dict) and data.get("error"):
                    raise ValueError(f"Hugging Face error: {data.get('error')}")
                raise ValueError(f"Unexpected Hugging Face response: {data}")
            except Exception:
                safe_prompt = requests.utils.quote(prompt)
                return f"https://image.pollinations.ai/prompt/{safe_prompt}"

        payload = {
            "model": "gpt-image-1",
            "prompt": image_prompt,
            "size": "1024x1024",
        }
        response = requests.post(
            self.cfg.image_api_base,
            json=payload,
            headers=headers,
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        return data["data"][0]["url"]

    @staticmethod
    def _is_real_token(token: str) -> bool:
        token = (token or "").strip()
        if not token:
            return False
        return "YOUR_" not in token

    @staticmethod
    def _resolve_hf_image_endpoint(image_api_base: str) -> str:
        legacy_prefix = "https://api-inference.huggingface.co/models/"
        if image_api_base.startswith(legacy_prefix):
            model_id = image_api_base[len(legacy_prefix) :]
            return f"https://router.huggingface.co/hf-inference/models/{model_id}"
        return image_api_base
