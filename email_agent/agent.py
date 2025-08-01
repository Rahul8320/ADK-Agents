from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

from pydantic import BaseModel,Field

class EmailContent(BaseModel):
    subject: str = Field(
        description="The subject line of the email. Should be concise and descriptive."
    )
    body: str = Field(
        description="The main content of the email. Should be well-formatted with proper greeting, paragraphs and signature."
    )

GENERATE_EMAIL_PROMPT = """
        You are an Email Generator Assistance.
        Your's task is to generate a professional email based on the user's request.

        GUIDELINES:
        - Create a appropriate subject line (concise and relevant)
        - Write a well-structured email body with:
            * Professional greeting
            * Clear and concise main content
            * Appropriate closing
            * Your name as signature
        - Suggest relevant attachments if applicable (empty list if none needed)
        - Email tone should match the purpose (formal for business, friendly for colleagues)
        - Keep email concise but complete

        IMPORTANT: Your response MUST be valid JSON matching this structure:
        {
            "subject": "Subject line here",
            "body": "Email body here with proper paragraph and formatting"
        }

        DO NOT include any explanation or additional text outside the JSON response.
    """

root_agent = LlmAgent(
    name="email_agent",
    description="Generate professional emails with structured subject and body",
    model=LiteLlm(model="ollama_chat/qwen3:1.7b"),
    instruction=GENERATE_EMAIL_PROMPT,
    output_schema=EmailContent,
    output_key="email"
)