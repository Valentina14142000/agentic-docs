# config/settings.py
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field, model_validator

load_dotenv()

DEFAULT_GEMINI_MODEL = "gemini-2.0-flash"


class Settings(BaseModel):
    # This field acts as the unified key holder for your agent parameters
    openai_api_key: str = Field(default="")
    model_name: str = Field(default=DEFAULT_GEMINI_MODEL)
    temperature: float = Field(default=0.2)

    @model_validator(mode="before")
    @classmethod
    def resolve_api_keys(cls, data: dict) -> dict:
        """
        Dynamically resolves the correct API key and model from .env.
        Prioritizes GEMINI_API_KEY first when running Gemini, falling back to OPENAI_API_KEY.
        """
        if not isinstance(data, dict):
            return data

        gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")

        resolved_key = data.get("openai_api_key") or gemini_key or openai_key or ""
        data["openai_api_key"] = resolved_key

        resolved_model = (
            data.get("model_name")
            or os.getenv("GEMINI_MODEL")
            or os.getenv("GOOGLE_MODEL")
            or os.getenv("GEMINI_MODEL_NAME")
            or os.getenv("GOOGLE_MODEL_NAME")
            or DEFAULT_GEMINI_MODEL
        )
        data["model_name"] = resolved_model or DEFAULT_GEMINI_MODEL
        return data

    @property
    def is_valid(self) -> bool:
        return bool(self.openai_api_key)

settings = Settings()