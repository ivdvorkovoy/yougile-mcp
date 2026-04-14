from __future__ import annotations

from typing import Any

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from .client import YouGileClient
from .config import Settings


mcp = FastMCP("yougile-mcp")


def _client() -> YouGileClient:
    settings = Settings.from_env()
    return YouGileClient(settings)


def _compact(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, dict):
        return {k: value[k] for k in value.keys()}
    if isinstance(value, list):
        return value
    return value


def _with_client(action):
    client = _client()
    try:
        return _compact(action(client))
    finally:
        client.close()


@mcp.tool()
def list_companies() -> Any:
    """List companies visible to the configured YouGile account."""
    client = _client()
    try:
        return _compact(client.list_companies())
    finally:
        client.close()


@mcp.tool()
def list_api_keys() -> Any:
    """List API keys for the configured company."""
    client = _client()
    try:
        return _compact(client.list_api_keys())
    finally:
        client.close()


@mcp.tool()
def delete_api_key(key: str) -> Any:
    """Delete an API key by value."""
    client = _client()
    try:
        return _compact(client.delete_api_key(key))
    finally:
        client.close()


@mcp.tool()
def list_projects() -> Any:
    """List accessible projects in YouGile."""
    return _with_client(lambda client: client.list_projects())


@mcp.tool()
def get_project(project_id: str) -> Any:
    """Get a project by id."""
    return _with_client(lambda client: client.get_project(project_id))


@mcp.tool()
def create_project(title: str, users: list[str] | None = None) -> Any:
    """Create a project."""
    payload: dict[str, Any] = {"title": title}
    if users:
        payload["users"] = users
    return _with_client(lambda client: client.create_project(payload))


@mcp.tool()
def update_project(project_id: str, title: str = "", users: list[str] | None = None, deleted: bool | None = None) -> Any:
    """Update a project."""
    payload: dict[str, Any] = {}
    if title:
        payload["title"] = title
    if users is not None:
        payload["users"] = users
    if deleted is not None:
        payload["deleted"] = deleted
    return _with_client(lambda client: client.update_project(project_id, payload))


@mcp.tool()
def list_boards() -> Any:
    """List boards."""
    return _with_client(lambda client: client.list_boards())


@mcp.tool()
def get_board(board_id: str) -> Any:
    """Get a board by id."""
    return _with_client(lambda client: client.get_board(board_id))


@mcp.tool()
def create_board(title: str, project_id: str, stickers: dict[str, Any] | None = None) -> Any:
    """Create a board."""
    payload: dict[str, Any] = {"title": title, "projectId": project_id}
    if stickers is not None:
        payload["stickers"] = stickers
    return _with_client(lambda client: client.create_board(payload))


@mcp.tool()
def update_board(board_id: str, title: str = "", project_id: str = "", stickers: dict[str, Any] | None = None, deleted: bool | None = None) -> Any:
    """Update a board."""
    payload: dict[str, Any] = {}
    if title:
        payload["title"] = title
    if project_id:
        payload["projectId"] = project_id
    if stickers is not None:
        payload["stickers"] = stickers
    if deleted is not None:
        payload["deleted"] = deleted
    return _with_client(lambda client: client.update_board(board_id, payload))


@mcp.tool()
def list_columns() -> Any:
    """List columns."""
    return _with_client(lambda client: client.list_columns())


@mcp.tool()
def get_column(column_id: str) -> Any:
    """Get a column by id."""
    return _with_client(lambda client: client.get_column(column_id))


@mcp.tool()
def create_column(title: str, board_id: str, color: int = 1) -> Any:
    """Create a column."""
    return _with_client(lambda client: client.create_column({"title": title, "boardId": board_id, "color": color}))


@mcp.tool()
def update_column(column_id: str, title: str = "", board_id: str = "", color: int | None = None, deleted: bool | None = None) -> Any:
    """Update a column."""
    payload: dict[str, Any] = {}
    if title:
        payload["title"] = title
    if board_id:
        payload["boardId"] = board_id
    if color is not None:
        payload["color"] = color
    if deleted is not None:
        payload["deleted"] = deleted
    return _with_client(lambda client: client.update_column(column_id, payload))


@mcp.tool()
def list_tasks(
    query: str = "",
    limit: int = 20,
    project_id: str | None = None,
    column_id: str | None = None,
    status: str | None = None,
) -> Any:
    """List tasks with optional filters."""
    params: dict[str, Any] = {"limit": limit}
    if query:
        params["query"] = query
    if project_id:
        params["projectId"] = project_id
    if column_id:
        params["columnId"] = column_id
    if status:
        params["status"] = status
    return _with_client(lambda client: client.list_tasks(params=params))


@mcp.tool()
def get_task(task_id: str) -> Any:
    """Get a single task by id."""
    return _with_client(lambda client: client.get_task(task_id))


@mcp.tool()
def create_task(
    title: str,
    project_id: str = "",
    column_id: str = "",
    description: str = "",
    assignee_id: str = "",
    due_date: str = "",
) -> Any:
    """Create a new task."""
    payload: dict[str, Any] = {"title": title}
    if project_id:
        payload["projectId"] = project_id
    if column_id:
        payload["columnId"] = column_id
    if description:
        payload["description"] = description
    if assignee_id:
        payload["assigneeId"] = assignee_id
    if due_date:
        payload["dueDate"] = due_date

    return _with_client(lambda client: client.create_task(payload))


@mcp.tool()
def update_task(
    task_id: str,
    title: str = "",
    description: str = "",
    status: str = "",
    assignee_id: str = "",
    column_id: str = "",
    due_date: str = "",
) -> Any:
    """Update an existing task."""
    payload: dict[str, Any] = {}
    if title:
        payload["title"] = title
    if description:
        payload["description"] = description
    if status:
        payload["status"] = status
    if assignee_id:
        payload["assigneeId"] = assignee_id
    if column_id:
        payload["columnId"] = column_id
    if due_date:
        payload["dueDate"] = due_date

    return _with_client(lambda client: client.update_task(task_id, payload))


@mcp.tool()
def add_comment(task_id: str, text: str) -> Any:
    """Add a comment to a task."""
    return _with_client(lambda client: client.add_comment(task_id, text))


@mcp.tool()
def search_tasks(query: str, limit: int = 20) -> Any:
    """Search tasks by text query."""
    return _with_client(lambda client: client.search_tasks(query, limit=limit))


@mcp.tool()
def get_task_chat_subscribers(task_id: str) -> Any:
    """Get subscribers for a task chat."""
    return _with_client(lambda client: client.get_task_chat_subscribers(task_id))


@mcp.tool()
def update_task_chat_subscribers(task_id: str, subscribers: dict[str, Any]) -> Any:
    """Update subscribers for a task chat."""
    return _with_client(lambda client: client.update_task_chat_subscribers(task_id, subscribers))


@mcp.tool()
def list_users() -> Any:
    """List users."""
    return _with_client(lambda client: client.list_users())


@mcp.tool()
def get_user(user_id: str) -> Any:
    """Get a user by id."""
    return _with_client(lambda client: client.get_user(user_id))


@mcp.tool()
def create_user(email: str, is_admin: bool = False) -> Any:
    """Create a user."""
    return _with_client(lambda client: client.create_user({"email": email, "isAdmin": is_admin}))


@mcp.tool()
def update_user(user_id: str, is_admin: bool | None = None) -> Any:
    """Update a user."""
    payload: dict[str, Any] = {}
    if is_admin is not None:
        payload["isAdmin"] = is_admin
    return _with_client(lambda client: client.update_user(user_id, payload))


@mcp.tool()
def delete_user(user_id: str) -> Any:
    """Delete a user."""
    return _with_client(lambda client: client.delete_user(user_id))


@mcp.tool()
def list_group_chats() -> Any:
    """List group chats."""
    return _with_client(lambda client: client.list_group_chats())


@mcp.tool()
def get_group_chat(chat_id: str) -> Any:
    """Get a group chat by id."""
    return _with_client(lambda client: client.get_group_chat(chat_id))


@mcp.tool()
def create_group_chat(title: str, users: list[str] | None = None, user_role_map: dict[str, Any] | None = None, role_config_map: dict[str, Any] | None = None) -> Any:
    """Create a group chat."""
    payload: dict[str, Any] = {"title": title}
    if users is not None:
        payload["users"] = users
    if user_role_map is not None:
        payload["userRoleMap"] = user_role_map
    if role_config_map is not None:
        payload["roleConfigMap"] = role_config_map
    return _with_client(lambda client: client.create_group_chat(payload))


@mcp.tool()
def update_group_chat(chat_id: str, title: str = "", users: list[str] | None = None, user_role_map: dict[str, Any] | None = None, role_config_map: dict[str, Any] | None = None, deleted: bool | None = None) -> Any:
    """Update a group chat."""
    payload: dict[str, Any] = {}
    if title:
        payload["title"] = title
    if users is not None:
        payload["users"] = users
    if user_role_map is not None:
        payload["userRoleMap"] = user_role_map
    if role_config_map is not None:
        payload["roleConfigMap"] = role_config_map
    if deleted is not None:
        payload["deleted"] = deleted
    return _with_client(lambda client: client.update_group_chat(chat_id, payload))


@mcp.tool()
def list_chat_messages(chat_id: str) -> Any:
    """List chat messages."""
    return _with_client(lambda client: client.list_chat_messages(chat_id))


@mcp.tool()
def get_chat_message(chat_id: str, message_id: str) -> Any:
    """Get a chat message by id."""
    return _with_client(lambda client: client.get_chat_message(chat_id, message_id))


@mcp.tool()
def create_chat_message(chat_id: str, text: str, text_html: str = "", label: str = "") -> Any:
    """Create a chat message."""
    payload: dict[str, Any] = {"text": text}
    if text_html:
        payload["textHtml"] = text_html
    if label:
        payload["label"] = label
    return _with_client(lambda client: client.create_chat_message(chat_id, payload))


@mcp.tool()
def update_chat_message(chat_id: str, message_id: str, text: str = "", text_html: str = "", label: str = "", deleted: bool | None = None, react: dict[str, Any] | None = None) -> Any:
    """Update a chat message."""
    payload: dict[str, Any] = {}
    if text:
        payload["text"] = text
    if text_html:
        payload["textHtml"] = text_html
    if label:
        payload["label"] = label
    if deleted is not None:
        payload["deleted"] = deleted
    if react is not None:
        payload["react"] = react
    return _with_client(lambda client: client.update_chat_message(chat_id, message_id, payload))


@mcp.tool()
def list_project_roles(project_id: str) -> Any:
    """List project roles."""
    return _with_client(lambda client: client.list_project_roles(project_id))


@mcp.tool()
def create_project_role(project_id: str, name: str, permissions: dict[str, Any], description: str = "") -> Any:
    """Create a project role."""
    payload: dict[str, Any] = {"name": name, "permissions": permissions}
    if description:
        payload["description"] = description
    return _with_client(lambda client: client.create_project_role(project_id, payload))


@mcp.tool()
def update_project_role(project_id: str, role_id: str, name: str = "", permissions: dict[str, Any] | None = None, description: str = "") -> Any:
    """Update a project role."""
    payload: dict[str, Any] = {}
    if name:
        payload["name"] = name
    if permissions is not None:
        payload["permissions"] = permissions
    if description:
        payload["description"] = description
    return _with_client(lambda client: client.update_project_role(project_id, role_id, payload))


@mcp.tool()
def delete_project_role(project_id: str, role_id: str) -> Any:
    """Delete a project role."""
    return _with_client(lambda client: client.delete_project_role(project_id, role_id))


@mcp.tool()
def list_departments() -> Any:
    """List departments."""
    return _with_client(lambda client: client.list_departments())


@mcp.tool()
def get_department(department_id: str) -> Any:
    """Get a department by id."""
    return _with_client(lambda client: client.get_department(department_id))


@mcp.tool()
def create_department(title: str, users: list[str] | None = None, deleted: bool | None = None) -> Any:
    """Create a department."""
    payload: dict[str, Any] = {"title": title}
    if users is not None:
        payload["users"] = users
    if deleted is not None:
        payload["deleted"] = deleted
    return _with_client(lambda client: client.create_department(payload))


@mcp.tool()
def update_department(department_id: str, title: str = "", users: list[str] | None = None, deleted: bool | None = None) -> Any:
    """Update a department."""
    payload: dict[str, Any] = {}
    if title:
        payload["title"] = title
    if users is not None:
        payload["users"] = users
    if deleted is not None:
        payload["deleted"] = deleted
    return _with_client(lambda client: client.update_department(department_id, payload))


@mcp.tool()
def list_sprint_stickers() -> Any:
    """List sprint stickers."""
    return _with_client(lambda client: client.list_sprint_stickers())


@mcp.tool()
def get_sprint_sticker(sticker_id: str) -> Any:
    """Get a sprint sticker by id."""
    return _with_client(lambda client: client.get_sprint_sticker(sticker_id))


@mcp.tool()
def create_sprint_sticker(name: str, states: list[dict[str, Any]] | None = None) -> Any:
    """Create a sprint sticker."""
    payload: dict[str, Any] = {"name": name}
    if states is not None:
        payload["states"] = states
    return _with_client(lambda client: client.create_sprint_sticker(payload))


@mcp.tool()
def update_sprint_sticker(sticker_id: str, name: str = "", deleted: bool | None = None) -> Any:
    """Update a sprint sticker."""
    payload: dict[str, Any] = {}
    if name:
        payload["name"] = name
    if deleted is not None:
        payload["deleted"] = deleted
    return _with_client(lambda client: client.update_sprint_sticker(sticker_id, payload))


@mcp.tool()
def list_sprint_sticker_states(sticker_id: str) -> Any:
    """List sprint sticker states."""
    return _with_client(lambda client: client.list_sprint_sticker_states(sticker_id))


@mcp.tool()
def get_sprint_sticker_state(sticker_id: str, state_id: str) -> Any:
    """Get a sprint sticker state by id."""
    return _with_client(lambda client: client.get_sprint_sticker_state(sticker_id, state_id))


@mcp.tool()
def create_sprint_sticker_state(sticker_id: str, name: str, begin: str = "", end: str = "") -> Any:
    """Create a sprint sticker state."""
    payload: dict[str, Any] = {"name": name}
    if begin:
        payload["begin"] = begin
    if end:
        payload["end"] = end
    return _with_client(lambda client: client.create_sprint_sticker_state(sticker_id, payload))


@mcp.tool()
def update_sprint_sticker_state(
    sticker_id: str,
    state_id: str,
    name: str = "",
    begin: str = "",
    end: str = "",
    deleted: bool | None = None,
) -> Any:
    """Update a sprint sticker state."""
    payload: dict[str, Any] = {}
    if name:
        payload["name"] = name
    if begin:
        payload["begin"] = begin
    if end:
        payload["end"] = end
    if deleted is not None:
        payload["deleted"] = deleted
    return _with_client(lambda client: client.update_sprint_sticker_state(sticker_id, state_id, payload))


@mcp.tool()
def list_string_stickers() -> Any:
    """List string stickers."""
    return _with_client(lambda client: client.list_string_stickers())


@mcp.tool()
def get_string_sticker(sticker_id: str) -> Any:
    """Get a string sticker by id."""
    return _with_client(lambda client: client.get_string_sticker(sticker_id))


@mcp.tool()
def create_string_sticker(name: str, icon: str = "", states: list[dict[str, Any]] | None = None) -> Any:
    """Create a string sticker."""
    payload: dict[str, Any] = {"name": name}
    if icon:
        payload["icon"] = icon
    if states is not None:
        payload["states"] = states
    return _with_client(lambda client: client.create_string_sticker(payload))


@mcp.tool()
def update_string_sticker(sticker_id: str, name: str = "", icon: str = "", deleted: bool | None = None) -> Any:
    """Update a string sticker."""
    payload: dict[str, Any] = {}
    if name:
        payload["name"] = name
    if icon:
        payload["icon"] = icon
    if deleted is not None:
        payload["deleted"] = deleted
    return _with_client(lambda client: client.update_string_sticker(sticker_id, payload))


@mcp.tool()
def list_string_sticker_states(sticker_id: str) -> Any:
    """List string sticker states."""
    return _with_client(lambda client: client.list_string_sticker_states(sticker_id))


@mcp.tool()
def get_string_sticker_state(sticker_id: str, state_id: str) -> Any:
    """Get a string sticker state by id."""
    return _with_client(lambda client: client.get_string_sticker_state(sticker_id, state_id))


@mcp.tool()
def create_string_sticker_state(sticker_id: str, name: str, color: str = "") -> Any:
    """Create a string sticker state."""
    payload: dict[str, Any] = {"name": name}
    if color:
        payload["color"] = color
    return _with_client(lambda client: client.create_string_sticker_state(sticker_id, payload))


@mcp.tool()
def update_string_sticker_state(
    sticker_id: str,
    state_id: str,
    name: str = "",
    color: str = "",
    deleted: bool | None = None,
) -> Any:
    """Update a string sticker state."""
    payload: dict[str, Any] = {}
    if name:
        payload["name"] = name
    if color:
        payload["color"] = color
    if deleted is not None:
        payload["deleted"] = deleted
    return _with_client(lambda client: client.update_string_sticker_state(sticker_id, state_id, payload))


@mcp.tool()
def list_event_subscriptions(include_deleted: bool = False) -> Any:
    """List event subscriptions."""
    return _with_client(lambda client: client.list_event_subscriptions(include_deleted=include_deleted))


@mcp.tool()
def get_event_subscription(subscription_id: str) -> Any:
    """Get an event subscription by id."""
    return _with_client(lambda client: client.get_event_subscription(subscription_id))


@mcp.tool()
def create_event_subscription(url: str, event: str, deleted: bool | None = None, secret: str = "") -> Any:
    """Create an event subscription."""
    payload: dict[str, Any] = {"url": url, "event": event}
    if deleted is not None:
        payload["deleted"] = deleted
    if secret:
        payload["secret"] = secret
    return _with_client(lambda client: client.create_event_subscription(payload))


@mcp.tool()
def update_event_subscription(subscription_id: str, url: str = "", event: str = "", deleted: bool | None = None, secret: str = "") -> Any:
    """Update an event subscription."""
    payload: dict[str, Any] = {}
    if url:
        payload["url"] = url
    if event:
        payload["event"] = event
    if deleted is not None:
        payload["deleted"] = deleted
    if secret:
        payload["secret"] = secret
    return _with_client(lambda client: client.update_event_subscription(subscription_id, payload))


@mcp.tool()
def delete_event_subscription(subscription_id: str) -> Any:
    """Delete an event subscription."""
    return _with_client(lambda client: client.delete_event_subscription(subscription_id))


def main() -> None:
    load_dotenv()
    mcp.run()


if __name__ == "__main__":
    main()
