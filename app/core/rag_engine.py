from google import genai
from google.genai import types

from app.config import settings
from app.core.tools import TOOLS

GENERATION_MODEL = "gemini-3.6-flash"
MAX_TOOL_CALL_ROUNDS = 5

_client = genai.Client(api_key=settings.gemini_api_key)


SYSTEM_INSTRUCTION = """\
Ты — ассистент, который отвечает на вопросы пользователя.
У тебя есть два инструмента:
- search_knowledge_base — используй его для вопросов о содержимом загруженного документа
- get_exchange_rate — используй его для вопросов о курсах валют

Если вопрос не требует инструментов (общие вопросы, приветствия) — отвечай напрямую.
Если нужного инструмента нет для ответа на вопрос — честно скажи об этом.
"""

async def generate_agentic_answer(
    question: str,
    tool_dispatch: dict,
) -> str:
    contents: list[types.Content] = [
        types.Content(role="user", parts=[types.Part.from_text(text=question)]),
    ]

    for _ in range(MAX_TOOL_CALL_ROUNDS):
        response = await _client.aio.models.generate_content(
            model=GENERATION_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                tools=[TOOLS],
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            ),
        )

        if not response.function_calls:
            return response.text

        contents.append(response.candidates[0].content)

        function_response_parts = []
        for function_call in response.function_calls:
            tool_fn = tool_dispatch.get(function_call.name)

            if tool_fn is None:
                result = {"error": f"Неизвестный инструмент: {function_call.name}"}
            else:
                try:
                    result = await tool_fn(**function_call.args)
                except Exception as exc:  # noqa: BLE001
                    result = {"error": str(exc)}

            function_response_parts.append(
                types.Part.from_function_response(name=function_call.name, response=result)
            )

        contents.append(types.Content(role="user", parts=function_response_parts))

    return "Не удалось сформировать ответ за отведённое количество шагов."