import json

from app.llm_service.domain.models import LLMContext, LLMResponse
from app.llm_service.ports.llm_port import LLMPort
from app.orchestrator.domain.proposed_action import ProposedAction

SYSTEM_PROMPT = """Eres Jarvis, un asistente de domótica e inteligencia personal.
Debes responder ÚNICAMENTE con JSON estructurado, sin texto adicional.

Acciones disponibles: {available_actions}

Contexto conocido:
{facts}

Historial reciente:
{history}

Instrucciones:
- Analiza la solicitud del usuario.
- Responde con el JSON exacto descrito abajo.
- Si la solicitud no es clara, usa action_type "query_info" para pedir aclaración.
- Acciones irreversibles: risk_level "high", requires_confirmation true.

Formato JSON requerido:
{{
  "source": "llm",
  "action_type": "device_control" | "query_info" | "notification" | "automation_change",
  "description": "explicación breve de la acción",
  "parameters": {{ ... }},
  "risk_level": "low" | "medium" | "high",
  "requires_confirmation": false
}}

Solicitud del usuario: {user_input}
"""


class LLMService:
    def __init__(self, llm: LLMPort):
        self._llm = llm

    def propose(self, context: LLMContext) -> LLMResponse:
        prompt = SYSTEM_PROMPT.format(
            available_actions=", ".join(context.available_actions),
            facts=_format_facts(context.facts),
            history=_format_history(context.recent_history),
            user_input=context.user_input,
        )

        try:
            raw = self._llm.generate(prompt)
        except Exception as e:
            return LLMResponse(
                raw_text="",
                error=f"LLM call failed: {e}",
            )

        action = self._parse_action(raw)
        if action:
            return LLMResponse(raw_text=raw, parsed_action=action)

        return LLMResponse(
            raw_text=raw,
            error="Could not parse LLM response as valid action JSON",
        )

    def _parse_action(self, raw: str) -> ProposedAction | None:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            return None

        try:
            return ProposedAction(**data)
        except Exception:
            return None


def _format_facts(facts: list[dict]) -> str:
    if not facts:
        return "No hay hechos conocidos."
    return "\n".join(f"- {f['key']}: {f['value']}" for f in facts)


def _format_history(history: list[dict]) -> str:
    if not history:
        return "No hay interacciones recientes."
    return "\n".join(
        f"- Usuario: {h.get('user_input', '')}"
        for h in history[-3:]
    )
