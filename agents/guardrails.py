import json
from typing import Any
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage


def input_guardrail_check(query: str, llm: Any) -> tuple[bool, str]:
    """Determine whether the input query is valid for travel planning."""
    guardrail_prompt = f"""
Determine whether the following request belongs to travel planning or travel
information. Valid requests can include destinations, flights, hotels, weather,
budgets, visas, transportation, sightseeing, food, packing, or itineraries.

Block clearly unrelated requests and requests asking for harmful or illegal
instructions. Do not block a valid travel request merely because some details
are missing.

Return strict JSON only:
{{
  "allowed": true,
  "reason": ""
}}

User request:
{query}
"""
    try:
        response = llm.invoke(
            [
                SystemMessage(
                    content=(
                        "You are the input guardrail for a travel-planning application. "
                        "Return strict JSON only."
                    )
                ),
                HumanMessage(content=guardrail_prompt),
            ]
        )
        text = str(response.content)
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            parsed = json.loads(text[start : end + 1])
            allowed = bool(parsed.get("allowed", True))
            reason = str(parsed.get("reason", "")).strip()
            return allowed, reason

        return True, "Guardrail validation fallback allowed the request."
    except Exception as exc:
        print(f"Guardrail fallback used: {exc}")
        return True, "Guardrail validation fallback allowed the request."


def guardrail_blocked_agent(state: dict[str, Any]) -> dict[str, Any]:
    """Node handler for requests blocked by input guardrail."""
    reason = state.get("final_response") or state.get("guardrail_reason") or (
        "This request was blocked by the travel input guardrail."
    )
    return {
        "final_response": reason,
        "messages": [AIMessage(content=reason)],
    }
