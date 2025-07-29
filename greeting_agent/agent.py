from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

from datetime import datetime

def get_current_time() -> dict:
    """
    Get the current time in the format YYYY-MM-DD HH:MM:SS
    """
    return {
        "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

root_agent = Agent(
    name="greeting_agent",
    description="Greeting Agent",
    model=LiteLlm(model="ollama_chat/llama3.2:1b"),
    instruction="""
    You are a helpful assistant that greets the user in respect to the current time.
    To get the current time, please use get_current_time tool.  
    Ask for the user's name and greet them by name.
    """,
    tools=[get_current_time]
)