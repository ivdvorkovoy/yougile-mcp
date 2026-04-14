from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


def _env(name: str, default: str = "") -> str:
    value = os.getenv(name, default)
    return value.strip()


@dataclass(frozen=True)
class Settings:
    base_url: str
    api_key: str
    email: str
    password: str
    company_id: str
    company_name: str
    company_id_path: str
    api_key_path: str
    api_key_list_path: str
    api_key_delete_path: str
    dotenv_path: Path
    timeout_seconds: float
    rate_limit_per_minute: int

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            base_url=_env("YOUGILE_BASE_URL", "https://your-domain.com"),
            api_key=_env("YOUGILE_API_KEY"),
            email=_env("YOUGILE_EMAIL"),
            password=_env("YOUGILE_PASSWORD"),
            company_id=_env("YOUGILE_COMPANY_ID"),
            company_name=_env("YOUGILE_COMPANY_NAME"),
            company_id_path=_env("YOUGILE_COMPANY_ID_PATH", "/api-v2/auth/companies"),
            api_key_path=_env("YOUGILE_API_KEY_PATH", "/api-v2/auth/keys"),
            api_key_list_path=_env("YOUGILE_API_KEY_LIST_PATH", "/api-v2/auth/keys/get"),
            api_key_delete_path=_env("YOUGILE_API_KEY_DELETE_PATH", "/api-v2/auth/keys"),
            dotenv_path=Path(_env("YOUGILE_DOTENV_PATH", ".env")),
            timeout_seconds=float(_env("YOUGILE_TIMEOUT_SECONDS", "30")),
            rate_limit_per_minute=int(_env("YOUGILE_RATE_LIMIT_PER_MINUTE", "50")),
        )
