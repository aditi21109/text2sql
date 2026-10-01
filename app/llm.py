import json
from typing import Type, TypeVar
from groq import Groq
from pydantic import BaseModel, ValidationError
from .config import settings

T = TypeVar("T", bound=BaseModel)

_client = Groq(api_key=settings.groq_api_key)

def ask(system: str, user: str, schema: Type[T], retries: int = 2) -> T:
    """LLM ko call karo aur validated Pydantic object wapas lo."""
    sys_prompt = (
        system
        + "\n\nRespond with ONLY a JSON object matching this JSON Schema:\n"
        + json.dumps(schema.model_json_schema())
    )
    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": user},
    ]
    for _ in range(retries + 1):
        resp = _client.chat.completions.create(
            model=settings.llm_model,
            messages=messages,
            temperature=0,
            response_format={"type": "json_object"},
        )
        text = resp.choices[0].message.content or ""
        try:
            return schema.model_validate_json(text)
        except ValidationError as e:
            messages += [
                {"role": "assistant", "content": text},
                {"role": "user", "content": f"Invalid output: {e}. Return corrected JSON only."},
            ]
    raise RuntimeError("LLM valid output nahi de paya")