#!/usr/bin/env python3

import logging
from typing import Dict, List, Optional
import os
import requests

logger = logging.getLogger(__name__)


class LLMValidator:
    """
    Validates PII detection results using OpenAI LLM to identify false positives.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini"
    ):
        """
        Initialize the LLM validator.

        Args:
            api_key: OpenAI API key (if None, uses OPENAI_API_KEY env var)
            model: OpenAI model to use for validation
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.api_url = "https://api.openai.com/v1/chat/completions"

        if not self.api_key:
            logger.warning("No OpenAI API key provided. LLM validation will be skipped.")

    def validate_entity(
        self,
        entity_type: str,
        secret_found: str,
        context: str,
        score: float,
        pattern_name: Optional[str] = None
    ) -> Dict:
        """
        Validate a single entity detection using LLM.
        """
        if not self.api_key:
            return {
                "is_true_positive": None,
                "reasoning": "LLM validation skipped - no API key provided",
                "validation_status": "skipped"
            }

        prompt = self._build_validation_prompt(
            entity_type, secret_found, context, score, pattern_name
        )

        try:
            response = self._call_openai_api(prompt)
            return self._parse_llm_response(response)
        except Exception as e:
            logger.error("LLM validation failed", exc_info=True)
            return {
                "is_true_positive": None,
                "reasoning": f"Validation error: {str(e)}",
                "validation_status": "error"
            }

    def _build_validation_prompt(
        self,
        entity_type: str,
        secret_found: str,
        context: str,
        score: float,
        pattern_name: Optional[str]
    ) -> str:
        """Build the prompt for LLM validation."""

        max_context_length = 500
        if len(context) > max_context_length:
            secret_pos = context.find(secret_found)
            if secret_pos != -1:
                start = max(0, secret_pos - 200)
                end = min(len(context), secret_pos + len(secret_found) + 200)
                context = "..." + context[start:end] + "..."
            else:
                context = context[:max_context_length] + "..."

        return f"""You are a PII (Personally Identifiable Information) validation expert.
Determine whether the detected entity is a TRUE POSITIVE (real PII) or FALSE POSITIVE.

Entity Detection Details:
- Entity Type: {entity_type}
- Detected Value: "{secret_found}"
- Detection Score: {score}
- Pattern Used: {pattern_name or 'N/A'}

Context:
{context}

Guidelines:
1. TRUE POSITIVE = real, sensitive PII that should be protected
2. FALSE POSITIVE includes:
   - Example or dummy data
   - Test placeholders
   - Dates matching SSN patterns
   - URLs matching email patterns
   - Column headers or field names
   - Coincidental regex matches
3. If unsure, choose UNCERTAIN
4. Do NOT invent or restate PII beyond what is shown

Response format (exactly):
DECISION: [TRUE_POSITIVE/FALSE_POSITIVE/UNCERTAIN]
REASONING: [One sentence explanation]
"""

    def _call_openai_api(self, prompt: str) -> str:
        """Call OpenAI Chat Completions API."""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,
            "max_tokens": 150
        }

        response = requests.post(
            self.api_url,
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()

        data = response.json()
        return data["choices"][0]["message"]["content"]

    def _parse_llm_response(self, response: str) -> Dict:
        """Parse the LLM response into structured output."""

        decision = None
        reasoning = ""

        for line in response.strip().splitlines():
            line = line.strip()
            if line.startswith("DECISION:"):
                value = line.split("DECISION:", 1)[1].strip()
                if value == "TRUE_POSITIVE":
                    decision = True
                elif value == "FALSE_POSITIVE":
                    decision = False
                else:
                    decision = None
            elif line.startswith("REASONING:"):
                reasoning = line.split("REASONING:", 1)[1].strip()

        if decision is None:
            status = "uncertain"
        elif decision:
            status = "validated"
        else:
            status = "false_positive"

        return {
            "is_true_positive": decision,
            "reasoning": reasoning,
            "validation_status": status,
            "llm_model": self.model
        }

    def validate_batch(
        self,
        detections: List[Dict],
        full_text: str,
        batch_size: Optional[int] = None
    ) -> List[Dict]:
        """
        Validate a batch of detections.
        """
        results = []

        for i, detection in enumerate(detections):
            if batch_size is not None and i >= batch_size:
                detection["llm_validation"] = {
                    "is_true_positive": None,
                    "reasoning": "Skipped - batch limit reached",
                    "validation_status": "skipped"
                }
                results.append(detection)
                continue

            start = detection.get("start", 0)
            end = detection.get("end", 0)

            context = full_text[max(0, start - 100): min(len(full_text), end + 100)]

            pattern_name = (
                detection.get("analysis_explanation", {}).get("pattern_name")
            )

            validation = self.validate_entity(
                entity_type=detection.get("entity_type", "UNKNOWN"),
                secret_found=detection.get("secret_found", ""),
                context=context,
                score=detection.get("score", 0.0),
                pattern_name=pattern_name
            )

            detection["llm_validation"] = validation
            results.append(detection)

            logger.info(
                f"Validated {detection.get('entity_type')} → {validation['validation_status']}"
            )

        return results
