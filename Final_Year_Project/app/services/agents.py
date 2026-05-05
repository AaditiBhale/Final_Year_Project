from __future__ import annotations

import os
import re
from typing import Dict, List

import requests

from app.services.vector_store import ManufacturingVectorStore


class AgenticManufacturingSystem:
    """
    Researcher + Writer hand-off workflow.
    Uses local retrieval first and can call an LLM when enabled.
    """

    def __init__(self, retriever: ManufacturingVectorStore) -> None:
        self.retriever = retriever
        self.use_mock_mode = os.getenv("USE_MOCK_MODE", "true").lower() == "true"
        self.llm_api_key = os.getenv("LLM_API_KEY", "")
        self.llm_api_base = os.getenv("LLM_API_BASE", "https://api.openai.com/v1")
        self.llm_model = os.getenv("LLM_MODEL", "gpt-4o-mini")

    def run(self, topic: str) -> Dict[str, object]:
        focus = self._extract_focus(topic)
        research_notes = self._researcher_agent(topic)
        final_report = self._writer_agent(topic, research_notes)
        return {
            "topic": topic,
            "detected_focus": focus,
            "research_notes": research_notes,
            "final_report": final_report,
        }

    def _researcher_agent(self, topic: str) -> List[str]:
        local_facts = self.retriever.retrieve(topic, top_k=4)
        focus = self._extract_focus(topic)
        if self.use_mock_mode or not self._is_real_token(self.llm_api_key):
            return [
                f"Program focus: {focus}. Build sourcing and operations baseline around this target.",
                f"{focus}: Evaluate tier-1 and tier-2 vendors for critical components and quality maturity.",
                "Risk factors: Lead time volatility for electronics and import-dependent materials.",
                "Cost controls: Batch procurement, component commonization, and dual-vendor agreements.",
                *local_facts[:2],
            ]

        prompt = (
            "Act as a manufacturing researcher. "
            f"Program focus under analysis: {focus}. "
            "Provide concise but specific bullet points for supplier sourcing, "
            "capacity planning, quality risks, and cost optimization. "
            "If the topic includes a model/product/program name, explicitly reference it in findings. "
            f"Topic: {topic}. "
            f"Use this context where relevant: {local_facts}"
        )
        try:
            notes = self._llm_call(prompt)
            return [line.strip("- ").strip() for line in notes.splitlines() if line.strip()]
        except Exception:
            return [
                "Supplier landscape: Evaluate regional machining vendors.",
                "Risk factors: Lead time volatility for semiconductors.",
                "Cost controls: Batch procurement and standardization.",
                *local_facts[:2],
            ]

    def _writer_agent(self, topic: str, notes: List[str]) -> str:
        focus = self._extract_focus(topic)
        if self.use_mock_mode or not self._is_real_token(self.llm_api_key):
            bullets = "\n".join([f"- {n}" for n in notes])
            return (
                f"# Manufacturing Strategy Report: {focus}\n\n"
                "## Program Context\n"
                f"- Input objective: {topic}\n"
                f"- Detected focus/model: {focus}\n\n"
                "## Executive Summary\n"
                "Specific supplier and operations strategy with clear sourcing, quality, "
                "and scale-up actions.\n\n"
                "## Research Findings\n"
                f"{bullets}\n\n"
                "## Tailored Recommendations\n"
                "1. Prioritize localization candidates for high-volume components.\n"
                "2. Add supplier readiness gates for PPAP and process capability.\n"
                "3. Create quarterly cost-down roadmap linked to volume ramp.\n\n"
                "## Recommended Next Steps\n"
                "1. Supplier scorecard validation.\n"
                "2. Pilot production quality gate.\n"
                "3. Scale-up readiness review.\n"
                "4. Executive review with sourcing and plant teams."
            )

        prompt = (
            "Act as a technical writer for manufacturing programs. "
            f"Write a specific report for this focus: {focus}. "
            "Convert these researcher notes into a well-structured markdown report with: "
            "Program Context (must show detected focus/model), Executive Summary, "
            "Key Findings, Tailored Recommendations, and 30-60-90 day action plan.\n"
            f"Topic: {topic}\nNotes: {notes}"
        )
        try:
            return self._llm_call(prompt)
        except Exception:
            bullets = "\n".join([f"- {n}" for n in notes])
            return (
                f"# Manufacturing Strategy Report: {topic}\n\n"
                "## Executive Summary\n"
                "Cross-functional manufacturing plan with resilient sourcing and "
                "prototype-to-production transition.\n\n"
                "## Research Findings\n"
                f"{bullets}\n\n"
                "## Recommended Next Steps\n"
                "1. Supplier scorecard validation.\n"
                "2. Pilot production quality gate.\n"
                "3. Scale-up readiness review."
            )

    def _llm_call(self, user_prompt: str) -> str:
        payload = {
            "model": self.llm_model,
            "messages": [
                {"role": "system", "content": "You are a manufacturing expert assistant."},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.3,
            "max_tokens": 900,
        }
        headers = {
            "Authorization": f"Bearer {self.llm_api_key}",
            "Content-Type": "application/json",
        }
        if "openrouter.ai" in self.llm_api_base:
            headers["HTTP-Referer"] = "http://localhost"
            headers["X-Title"] = "Integrated Manufacturing AI Platform"
        response = requests.post(
            f"{self.llm_api_base}/chat/completions",
            json=payload,
            headers=headers,
            timeout=45,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    @staticmethod
    def _is_real_token(token: str) -> bool:
        token = (token or "").strip()
        if not token:
            return False
        return "YOUR_" not in token

    @staticmethod
    def _extract_focus(topic: str) -> str:
        quoted = re.findall(r"['\"]([^'\"]{2,60})['\"]", topic)
        if quoted:
            return quoted[0].strip()

        model_like = re.findall(r"\b[A-Za-z]+[- ]?[A-Za-z]*\s?(?:[A-Z]{1,3}\d{1,4}|\d{1,4}[A-Za-z]{0,3}|Mk\d+)\b", topic)
        if model_like:
            return model_like[0].strip()

        brands_or_programs = [
            "suzuki",
            "toyota",
            "hyundai",
            "tata",
            "mahindra",
            "honda",
            "kia",
            "drone",
            "robotic arm",
            "ev battery",
            "conveyor",
        ]
        lowered = topic.lower()
        for key in brands_or_programs:
            if key in lowered:
                return key.title()

        return "General Manufacturing Program"
