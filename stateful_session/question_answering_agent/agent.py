from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm

MODEL = LiteLlm(model="ollama_chat/qwen3:1.7b")

AGENT_PROMPT = """
    You are a helpful assistant that answers questions about the user's preferences.
    
    Here is some information about the user:
    Name:
    {user_name}
    Preferences:
    {user_preferences}
"""

# Create the root agent
question_answering_agent = Agent(
    name="question_answering_agent",
    model=MODEL,
    description="Question answering agent",
    instruction=AGENT_PROMPT,
)
