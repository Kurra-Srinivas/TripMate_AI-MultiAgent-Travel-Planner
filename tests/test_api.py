import sys
from pathlib import Path

# Ensure project root directory is in sys.path when running script directly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.tavily_tool import tavily_search
from tools.flight_tool import search_flights
from backend import run_travel_agent


if __name__ == "__main__":
    user_input = input("Enter travel request: ")

    response = run_travel_agent(
        user_input=user_input,
        thread_id="test_user"
    )

    print("\nFINAL RESPONSE:\n")
    print(response.get("answer", response))