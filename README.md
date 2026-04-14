# YouGile MCP starter

Minimal MCP server for YouGile built as a thin wrapper over the REST API.

## What this starter includes

- HTTP client with shared request/error handling
- API-key based auth support
- MCP tools for common task workflows
- Env-driven config

## Suggested MVP tools

- `list_companies`
- `list_api_keys`
- `delete_api_key`
- `get_project`
- `create_project`
- `update_project`
- `list_boards`
- `get_board`
- `create_board`
- `update_board`
- `list_columns`
- `get_column`
- `create_column`
- `update_column`
- `list_projects`
- `list_tasks`
- `get_task`
- `create_task`
- `update_task`
- `add_comment`
- `search_tasks`
- `list_users`
- `get_user`
- `create_user`
- `update_user`
- `delete_user`
- `list_group_chats`
- `get_group_chat`
- `create_group_chat`
- `update_group_chat`
- `list_chat_messages`
- `get_chat_message`
- `create_chat_message`
- `update_chat_message`
- `list_project_roles`
- `create_project_role`
- `update_project_role`
- `delete_project_role`
- `list_sprint_stickers`
- `get_sprint_sticker`
- `create_sprint_sticker`
- `update_sprint_sticker`
- `list_sprint_sticker_states`
- `get_sprint_sticker_state`
- `create_sprint_sticker_state`
- `update_sprint_sticker_state`
- `list_string_stickers`
- `get_string_sticker`
- `create_string_sticker`
- `update_string_sticker`
- `list_string_sticker_states`
- `get_string_sticker_state`
- `create_string_sticker_state`
- `update_string_sticker_state`
- `get_task_chat_subscribers`
- `update_task_chat_subscribers`

## Setup

1. Copy `.env.example` to `.env`
2. Fill `YOUGILE_BASE_URL`
3. Set either:
- `YOUGILE_API_KEY`, or
- `YOUGILE_EMAIL` + `YOUGILE_PASSWORD` + `YOUGILE_COMPANY_ID`
   - optionally `YOUGILE_COMPANY_NAME` if you belong to multiple companies
4. Install dependencies
5. Run the server

## Notes

- YouGile REST API uses `Authorization: Bearer <api_key>`.
- Official docs expose `POST /api-v2/auth/companies` for company lookup and `POST /api-v2/auth/keys` for API-key generation.
- On first successful login, the server will try to write the generated API key back into `.env`.
- If your deployment uses different auth paths, override them with the env vars in `.env.example`.
