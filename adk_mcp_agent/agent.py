from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm

from .prompt import MCP_AGENT_PROMPT

AGENT_MODEL: LiteLlm = LiteLlm(model="openai/qwen/qwen3-4b-2507")


root_agent = Agent(
    name="adk_mcp_agent",
    description="You are a helpful Agent",
    model=AGENT_MODEL,
    instruction=MCP_AGENT_PROMPT,
)
