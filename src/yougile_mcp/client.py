from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import time
from pathlib import Path
from typing import Any, Optional

import httpx

from .config import Settings


class YouGileError(RuntimeError):
    pass


@dataclass
class RateLimiter:
    limit_per_minute: int

    def __post_init__(self) -> None:
        self._calls = deque()

    def wait(self) -> None:
        if self.limit_per_minute <= 0:
            return

        now = time.monotonic()
        window_start = now - 60.0
        while self._calls and self._calls[0] < window_start:
            self._calls.popleft()

        if len(self._calls) >= self.limit_per_minute:
            sleep_for = 60.0 - (now - self._calls[0])
            if sleep_for > 0:
                time.sleep(sleep_for)
            self.wait()
            return

        self._calls.append(time.monotonic())


class YouGileClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._limiter = RateLimiter(settings.rate_limit_per_minute)
        self._client = httpx.Client(
            base_url=self._normalize_base_url(settings.base_url),
            timeout=httpx.Timeout(settings.timeout_seconds, connect=max(settings.timeout_seconds, 60.0)),
            headers={"Accept": "application/json"},
        )
        self._api_key: Optional[str] = settings.api_key or None

    @staticmethod
    def _normalize_base_url(base_url: str) -> str:
        return base_url.rstrip("/")

    def close(self) -> None:
        self._client.close()

    def ensure_api_key(self) -> str:
        if self._api_key:
            return self._api_key

        if not (self.settings.email and self.settings.password):
            raise YouGileError(
                "Set YOUGILE_API_KEY or provide YOUGILE_EMAIL, YOUGILE_PASSWORD and YOUGILE_COMPANY_ID."
            )

        company_id = self.settings.company_id or self.get_company_id()
        self._api_key = self.generate_api_key(company_id)
        self._persist_api_key(company_id, self._api_key)
        return self._api_key

    def get_company_id(self) -> str:
        payload = {
            "login": self.settings.email,
            "password": self.settings.password,
        }
        data = self._request(
            "POST",
            self.settings.company_id_path,
            json=payload,
            auth=False,
        )

        companies = []
        if isinstance(data, dict):
            companies = data.get("content") or []

        if not companies:
            raise YouGileError("Could not find any companies in auth response.")

        if self.settings.company_name:
            for company in companies:
                if str(company.get("name", "")).strip().lower() == self.settings.company_name.strip().lower():
                    return str(company["id"])

        if len(companies) == 1:
            return str(companies[0]["id"])

        available = ", ".join(str(company.get("name") or company.get("id")) for company in companies)
        raise YouGileError(
            "Multiple companies are available. Set YOUGILE_COMPANY_NAME or YOUGILE_COMPANY_ID. "
            f"Available: {available}"
        )

    def generate_api_key(self, company_id: str) -> str:
        payload = {
            "login": self.settings.email,
            "password": self.settings.password,
            "companyId": company_id,
        }
        data = self._request(
            "POST",
            self.settings.api_key_path,
            json=payload,
            auth=False,
        )

        api_key = self._pick(data, ("apiKey", "key", "token", "value"))
        if not api_key:
            raise YouGileError("Could not find api key in auth response.")
        return str(api_key)

    def request(self, method: str, resource: str, *, params: dict[str, Any] | None = None, json: Any = None) -> Any:
        return self._request(method, self._resource_path(resource), params=params, json=json)

    @staticmethod
    def _merge_params(*parts: dict[str, Any] | None) -> dict[str, Any]:
        params: dict[str, Any] = {}
        for part in parts:
            if not part:
                continue
            for key, value in part.items():
                if value is None or value == "":
                    continue
                params[key] = value
        return params

    def _request_collection(
        self,
        resource: str,
        *,
        params: dict[str, Any] | None = None,
        search: bool = False,
        reversed_search: bool = False,
    ) -> Any:
        if search:
            candidates = self._collection_search_paths(resource, reversed_search=reversed_search)
            for path in candidates:
                try:
                    return self.request("GET", path, params=params)
                except YouGileError as exc:
                    if "404" not in str(exc):
                        raise
            # Fall back to the plain collection endpoint if the search endpoint is not available.
        return self.request("GET", resource, params=params)

    @staticmethod
    def _collection_search_paths(resource: str, *, reversed_search: bool = False) -> list[str]:
        if reversed_search:
            return [
                f"{resource}/searchReversed",
                f"{resource}/search-reversed",
                f"{resource}/search/reversed",
            ]
        return [f"{resource}/search"]

    def list_projects(self, *, page: int | None = None, limit: int | None = None) -> Any:
        params = self._merge_params({"page": page, "limit": limit})
        return self._request_collection("projects", params=params, search=page is not None or limit is not None)

    def get_project(self, project_id: str) -> Any:
        return self.request("GET", f"projects/{project_id}")

    def create_project(self, payload: dict[str, Any]) -> Any:
        return self.request("POST", "projects", json=payload)

    def update_project(self, project_id: str, payload: dict[str, Any]) -> Any:
        return self.request("PUT", f"projects/{project_id}", json=payload)

    def list_boards(self, *, page: int | None = None, limit: int | None = None) -> Any:
        params = self._merge_params({"page": page, "limit": limit})
        return self._request_collection("boards", params=params, search=page is not None or limit is not None)

    def get_board(self, board_id: str) -> Any:
        return self.request("GET", f"boards/{board_id}")

    def create_board(self, payload: dict[str, Any]) -> Any:
        return self.request("POST", "boards", json=payload)

    def update_board(self, board_id: str, payload: dict[str, Any]) -> Any:
        return self.request("PUT", f"boards/{board_id}", json=payload)

    def list_columns(self, *, page: int | None = None, limit: int | None = None) -> Any:
        params = self._merge_params({"page": page, "limit": limit})
        return self._request_collection("columns", params=params, search=page is not None or limit is not None)

    def get_column(self, column_id: str) -> Any:
        return self.request("GET", f"columns/{column_id}")

    def create_column(self, payload: dict[str, Any]) -> Any:
        return self.request("POST", "columns", json=payload)

    def update_column(self, column_id: str, payload: dict[str, Any]) -> Any:
        return self.request("PUT", f"columns/{column_id}", json=payload)

    def list_tasks(self, *, params: dict[str, Any] | None = None) -> Any:
        return self.request("GET", "tasks", params=params)

    def get_task(self, task_id: str) -> Any:
        return self.request("GET", f"tasks/{task_id}")

    def create_task(self, payload: dict[str, Any]) -> Any:
        return self.request("POST", "tasks", json=payload)

    def update_task(self, task_id: str, payload: dict[str, Any]) -> Any:
        return self.request("PUT", f"tasks/{task_id}", json=payload)

    def add_comment(self, task_id: str, text: str) -> Any:
        return self.request("POST", f"tasks/{task_id}/comments", json={"text": text})

    def search_tasks(
        self,
        query: str,
        *,
        page: int | None = None,
        limit: int | None = 20,
        reversed_search: bool = False,
        project_id: str | None = None,
        column_id: str | None = None,
        status: str | None = None,
    ) -> Any:
        params = self._merge_params(
            {"query": query, "page": page, "limit": limit},
            {"projectId": project_id, "columnId": column_id, "status": status},
        )
        return self._request_collection("tasks", params=params, search=True, reversed_search=reversed_search)

    def get_task_chat_subscribers(self, task_id: str) -> Any:
        return self.request("GET", f"tasks/{task_id}/chat-subscribers")

    def update_task_chat_subscribers(self, task_id: str, payload: dict[str, Any]) -> Any:
        return self.request("PUT", f"tasks/{task_id}/chat-subscribers", json=payload)

    def list_companies(self) -> Any:
        payload = {
            "login": self.settings.email,
            "password": self.settings.password,
        }
        return self._request("POST", self.settings.company_id_path, json=payload, auth=False)

    def list_api_keys(self) -> Any:
        payload = {
            "login": self.settings.email,
            "password": self.settings.password,
            "companyId": self.settings.company_id or self.get_company_id(),
        }
        return self._request("POST", self.settings.api_key_list_path, json=payload, auth=False)

    def delete_api_key(self, key: str) -> Any:
        return self._request("DELETE", f"{self.settings.api_key_delete_path.rstrip('/')}/{key}", auth=False)

    def list_users(self) -> Any:
        return self.request("GET", "users")

    def get_user(self, user_id: str) -> Any:
        return self.request("GET", f"users/{user_id}")

    def create_user(self, payload: dict[str, Any]) -> Any:
        return self.request("POST", "users", json=payload)

    def update_user(self, user_id: str, payload: dict[str, Any]) -> Any:
        return self.request("PUT", f"users/{user_id}", json=payload)

    def delete_user(self, user_id: str) -> Any:
        return self.request("DELETE", f"users/{user_id}")

    def list_group_chats(self) -> Any:
        return self.request("GET", "group-chats")

    def get_group_chat(self, chat_id: str) -> Any:
        return self.request("GET", f"group-chats/{chat_id}")

    def create_group_chat(self, payload: dict[str, Any]) -> Any:
        return self.request("POST", "group-chats", json=payload)

    def update_group_chat(self, chat_id: str, payload: dict[str, Any]) -> Any:
        return self.request("PUT", f"group-chats/{chat_id}", json=payload)

    def list_chat_messages(self, chat_id: str) -> Any:
        return self.request("GET", f"chats/{chat_id}/messages")

    def get_chat_message(self, chat_id: str, message_id: str) -> Any:
        return self.request("GET", f"chats/{chat_id}/messages/{message_id}")

    def create_chat_message(self, chat_id: str, payload: dict[str, Any]) -> Any:
        return self.request("POST", f"chats/{chat_id}/messages", json=payload)

    def update_chat_message(self, chat_id: str, message_id: str, payload: dict[str, Any]) -> Any:
        return self.request("PUT", f"chats/{chat_id}/messages/{message_id}", json=payload)

    def list_project_roles(self, project_id: str) -> Any:
        return self.request("GET", f"projects/{project_id}/roles")

    def create_project_role(self, project_id: str, payload: dict[str, Any]) -> Any:
        return self.request("POST", f"projects/{project_id}/roles", json=payload)

    def update_project_role(self, project_id: str, role_id: str, payload: dict[str, Any]) -> Any:
        return self.request("PUT", f"projects/{project_id}/roles/{role_id}", json=payload)

    def delete_project_role(self, project_id: str, role_id: str) -> Any:
        return self.request("DELETE", f"projects/{project_id}/roles/{role_id}")

    def list_departments(self) -> Any:
        return self.request("GET", "departments")

    def get_department(self, department_id: str) -> Any:
        return self.request("GET", f"departments/{department_id}")

    def create_department(self, payload: dict[str, Any]) -> Any:
        return self.request("POST", "departments", json=payload)

    def update_department(self, department_id: str, payload: dict[str, Any]) -> Any:
        return self.request("PUT", f"departments/{department_id}", json=payload)

    def list_sprint_stickers(self, *, page: int | None = None, limit: int | None = None) -> Any:
        params = self._merge_params({"page": page, "limit": limit})
        return self._request_collection("sprint-stickers", params=params, search=page is not None or limit is not None)

    def get_sprint_sticker(self, sticker_id: str) -> Any:
        return self.request("GET", f"sprint-stickers/{sticker_id}")

    def create_sprint_sticker(self, payload: dict[str, Any]) -> Any:
        return self.request("POST", "sprint-stickers", json=payload)

    def update_sprint_sticker(self, sticker_id: str, payload: dict[str, Any]) -> Any:
        return self.request("PUT", f"sprint-stickers/{sticker_id}", json=payload)

    def list_sprint_sticker_states(self, sticker_id: str) -> Any:
        return self.request("GET", f"sprint-stickers/{sticker_id}/states")

    def get_sprint_sticker_state(self, sticker_id: str, state_id: str) -> Any:
        return self.request("GET", f"sprint-stickers/{sticker_id}/states/{state_id}")

    def create_sprint_sticker_state(self, sticker_id: str, payload: dict[str, Any]) -> Any:
        return self.request("POST", f"sprint-stickers/{sticker_id}/states", json=payload)

    def update_sprint_sticker_state(self, sticker_id: str, state_id: str, payload: dict[str, Any]) -> Any:
        return self.request("PUT", f"sprint-stickers/{sticker_id}/states/{state_id}", json=payload)

    def list_string_stickers(self, *, page: int | None = None, limit: int | None = None) -> Any:
        params = self._merge_params({"page": page, "limit": limit})
        return self._request_collection("string-stickers", params=params, search=page is not None or limit is not None)

    def get_string_sticker(self, sticker_id: str) -> Any:
        return self.request("GET", f"string-stickers/{sticker_id}")

    def create_string_sticker(self, payload: dict[str, Any]) -> Any:
        return self.request("POST", "string-stickers", json=payload)

    def update_string_sticker(self, sticker_id: str, payload: dict[str, Any]) -> Any:
        return self.request("PUT", f"string-stickers/{sticker_id}", json=payload)

    def list_string_sticker_states(self, sticker_id: str) -> Any:
        return self.request("GET", f"string-stickers/{sticker_id}/states")

    def get_string_sticker_state(self, sticker_id: str, state_id: str) -> Any:
        return self.request("GET", f"string-stickers/{sticker_id}/states/{state_id}")

    def create_string_sticker_state(self, sticker_id: str, payload: dict[str, Any]) -> Any:
        return self.request("POST", f"string-stickers/{sticker_id}/states", json=payload)

    def update_string_sticker_state(self, sticker_id: str, state_id: str, payload: dict[str, Any]) -> Any:
        return self.request("PUT", f"string-stickers/{sticker_id}/states/{state_id}", json=payload)

    def list_event_subscriptions(self, include_deleted: bool = False) -> Any:
        return self.request("GET", "webhooks", params={"includeDeleted": str(include_deleted).lower()})

    def get_event_subscription(self, subscription_id: str) -> Any:
        subscriptions = self.list_event_subscriptions(include_deleted=True)
        if isinstance(subscriptions, dict):
            content = subscriptions.get("content") or subscriptions.get("data") or subscriptions.get("items") or []
            for subscription in content:
                if str(subscription.get("id")) == subscription_id:
                    return subscription
        elif isinstance(subscriptions, list):
            for subscription in subscriptions:
                if str(subscription.get("id")) == subscription_id:
                    return subscription
        return None

    def create_event_subscription(self, payload: dict[str, Any]) -> Any:
        return self.request("POST", "webhooks", json=payload)

    def update_event_subscription(self, subscription_id: str, payload: dict[str, Any]) -> Any:
        return self.request("PUT", f"webhooks/{subscription_id}", json=payload)

    def delete_event_subscription(self, subscription_id: str) -> Any:
        return self.update_event_subscription(subscription_id, {"deleted": True})

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,
        auth: bool = True,
    ) -> Any:
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                self._limiter.wait()
                headers = {}
                if auth:
                    headers["Authorization"] = f"Bearer {self.ensure_api_key()}"

                response = self._client.request(method, path, params=params, json=json, headers=headers)

                if response.status_code >= 400:
                    raise YouGileError(self._format_error(response))

                if not response.content:
                    return None

                content_type = response.headers.get("content-type", "")
                if "application/json" in content_type:
                    return response.json()

                return response.text
            except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.ConnectError) as exc:
                last_error = exc
                if attempt < 2:
                    time.sleep(1.5 * (attempt + 1))
                    continue
                raise YouGileError(f"YouGile connection error for {method} {path}: {exc}") from exc

        if last_error is not None:
            raise YouGileError(f"YouGile connection error for {method} {path}: {last_error}") from last_error
        raise YouGileError(f"YouGile connection error for {method} {path}")

    @staticmethod
    def _resource_path(resource: str) -> str:
        return f"/api-v2/{resource.lstrip('/')}"

    @staticmethod
    def _pick(data: Any, keys: tuple[str, ...]) -> Any:
        if isinstance(data, dict):
            for key in keys:
                if key in data and data[key] not in (None, ""):
                    return data[key]
        return None

    @staticmethod
    def _format_error(response: httpx.Response) -> str:
        body: str
        try:
            parsed = response.json()
            if isinstance(parsed, dict) and parsed.get("error"):
                body = str(parsed["error"])
            else:
                body = response.text
        except Exception:
            body = response.text
        return f"YouGile API error {response.status_code} for {response.request.method} {response.request.url}: {body}"

    def _persist_api_key(self, company_id: str, api_key: str) -> None:
        path = self.settings.dotenv_path
        try:
            lines: list[str] = []
            if path.exists():
                lines = path.read_text(encoding="utf-8").splitlines()

            updated = {
                "YOUGILE_BASE_URL": self.settings.base_url,
                "YOUGILE_API_KEY": api_key,
                "YOUGILE_COMPANY_ID": company_id,
            }

            keep: list[str] = []
            seen = set()
            for line in lines:
                stripped = line.strip()
                if not stripped or stripped.startswith("#") or "=" not in line:
                    keep.append(line)
                    continue
                name, _ = line.split("=", 1)
                name = name.strip()
                if name in updated:
                    keep.append(f"{name}={updated[name]}")
                    seen.add(name)
                else:
                    keep.append(line)

            for name, value in updated.items():
                if name not in seen:
                    keep.append(f"{name}={value}")

            path.write_text("\n".join(keep) + "\n", encoding="utf-8")
        except Exception:
            # Persisting the key is a convenience, not a hard requirement.
            pass
