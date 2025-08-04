from typing import Dict, List

from google.adk.tools import ToolContext

from constants import REMINDERS


def add_reminder(reminder: str, tool_context: ToolContext) -> Dict:
    """
    Add a new reminder to the user's reminder list.

    Args:
        reminder(str): The reminder text to add
        tool_context(ToolContext): Context for accessing and updating session state

    Returns:
        A confirmation message with added reminder
    """
    print(f"============== Tool: add_reminder called for '{reminder}' ==============")

    # Get current reminders from state
    reminders: List = tool_context.state.get(REMINDERS, [])

    reminders.append(reminder)
    tool_context.state[REMINDERS] = reminders

    return {
        "action": "add_reminder",
        "reminder": reminder,
        "message": f"Added reminder: {reminder}",
    }