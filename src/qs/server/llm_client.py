from openai import OpenAI
from qs.server import get_settings

settings = get_settings()
client = OpenAI(api_key=settings.openai.api_key)


def call_llm(system_prompt: str, user_prompt: str) -> str:
    response = client.responses.create(
        model="gpt-5-nano",
        input=[
            {
                "role": "developer",
                "content": [{"type": "input_text", "text": system_prompt}],
            },
            {"role": "user", "content": [
                {"type": "input_text", "text": user_prompt}]},
        ],
        text={"format": {"type": "text"}, "verbosity": "medium"},
        reasoning={"effort": "medium", "summary": "auto"},
        tools=[],
        store=False,
        include=["reasoning.encrypted_content",
                 "web_search_call.action.sources"],
    )

    return response.output_text


def call_llm_chat(messages: list) -> str:
    response = client.responses.create(
        model="gpt-5-nano",
        input=[
            {
                "role": message.role if hasattr(message, 'role') else message["role"],
                "content": message.content if hasattr(message, 'content') else message["content"]
            }
            for message in messages
        ],
        text={"format": {"type": "text"}, "verbosity": "medium"},
        reasoning={"effort": "medium", "summary": "auto"},
        tools=[],
        store=False,
        include=["reasoning.encrypted_content",
                 "web_search_call.action.sources"],
    )

    return response.output_text
