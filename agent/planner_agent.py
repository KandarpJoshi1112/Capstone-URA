# agent/planner_agent.py
"""
PlannerAgent stub. In a full implementation, this would call LLM via llm_interface to
produce a plan from user intent. Provided as a simple synchronous placeholder.
"""
from typing import Dict, Any
from utils.logger import setup_logger

logger = setup_logger("planner_agent", None)

class PlannerAgent:
    def __init__(self):
        logger.info("PlannerAgent initialized")

    def plan_from_intent(self, intent: str) -> Dict[str, Any]:
        # Simple stub for the purpose of the Capstone minimal run
        logger.info("PlannerAgent received intent: %s", intent)
        return {"intent": intent, "steps": ["check_calendar", "check_weather", "notify_user"]}
