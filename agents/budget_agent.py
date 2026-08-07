from typing import Any
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage


def budget_agent(state: dict[str, Any], llm: Any = None) -> dict[str, Any]:
    """
    Budget agent node. Analyzes cost estimates, budget risks, and overall trip financial feasibility.
    """
    if llm is None:
        from mcp_client import llm as default_llm
        llm = default_llm

    prompt = f"""
Analyze whether this trip is realistic for the user's budget.

User Query:
{state['user_query']}

Trip Constraints:
{state.get('trip_constraints', {})}

Flight Results:
{state.get('flight_results', '')}

Hotel Results:
{state.get('hotel_results', '')}

Weather Results:
{state.get('weather_results', '')}

Return:
1. Estimated cost categories
2. Budget risk areas
3. Money-saving suggestions
4. Overall feasibility

If exact live prices are unavailable, clearly label estimates as approximate.
"""

    response = llm.invoke(
        [
            SystemMessage(content="You are a practical travel budget analyst."),
            HumanMessage(content=prompt),
        ]
    )

    return {
        "budget_results": str(response.content),
        "messages": [AIMessage(content="Budget assessment generated.")],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }
