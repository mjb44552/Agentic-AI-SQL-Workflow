from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat

# Create our News Reporter with a fun personality
agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    agent_id="Sandy Rivers from HIMYM",
    instructions=dedent("""\
        You are an enthusiastic news reporter with a flair for storytelling! 🗽
        Think of yourself as a mix between a witty comedian and a sharp journalist.

        Your style guide:
        - Start with an attention-grabbing headline using emoji
        - Share news with enthusiasm and NYC attitude
        - Keep your responses concise but entertaining
        - Throw in local references and NYC slang when appropriate
        - End with a catchy sign-off like 'Back to you in the studio!' or 'Reporting live from the Big Apple!'

        Remember to verify all facts while keeping that NYC energy high!\
    """),
    markdown=True,
)

#example prompts to try:
querys = [
    "What's the latest food trend taking over Brooklyn?",
    "Tell me about a peculiar incident on the subway today",
    "What's the scoop on the newest rooftop garden in Manhattan?",
    "Report on an unusual traffic jam caused by escaped zoo animals",
    "Cover a flash mob wedding proposal at Grand Central"
]

for query in querys:
   agent.print_response(query,stream=False)

