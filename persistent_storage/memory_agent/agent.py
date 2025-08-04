from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm

from memory_agent.tools.view_reminders_tool import view_reminders
from memory_agent.tools.add_reminder_tool import add_reminder
from memory_agent.prompt import MEMORY_AGENT_PROMPT

MODEL = LiteLlm(model="ollama_chat/qwen3:1.7b")

def get_memory_agent() -> Agent:
    return Agent(
        name="memory_agent",
        description="A start reminder agent with persistent memory",
        model=MODEL,
        instruction=MEMORY_AGENT_PROMPT,
        tools=[
            add_reminder,
            view_reminders
        ]
    )