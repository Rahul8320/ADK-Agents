from typing import List, Dict

from google.adk.tools import ToolContext

from constants import REMINDERS


def view_reminders(tool_context: ToolContext) -> Dict:
    """
    View all current reminders.

    Args:
        tool_context(ToolContext): Context for accessing session state

    Returns:
        The list of reminders
    """
    print(f"============== Tool: view_reminders called ==============")

    # Get current reminders from state
    reminders: List = tool_context.state.get(REMINDERS, [])

    return {
        "action": "view_reminders",
        "reminders": reminders,
        "count": len(reminders),
    }