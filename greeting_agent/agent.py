from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

root_agent = Agent(
    name="greeting_agent",
    description="Greeting Agent",
    model=LiteLlm(model="ollama_chat/llama3.2:1b"),
    instruction="""
    You are a helpful assistant that greets the user.
    Ask for the user's name and greet them by name.
    """
)