# YouGile MCP client config

Сервер поднят на Linux-машине и доступен по HTTP MCP endpoint:

- `http://192.10.10.160:3333/mcp`

## Generic MCP server entry

```json
{
  "mcpServers": {
    "yougile": {
      "url": "http://192.10.10.160:3333/mcp"
    }
  }
}
```

## Notes

- Сервер работает как `streamable-http`.
- Доступ к YouGile идёт напрямую с Linux-машины.
- Секреты по-прежнему хранятся локально в `~/yougile-mcp-starter/.env`.

## Available tools

- `list_companies`
- `list_api_keys`
- `delete_api_key`
- `list_projects`
- `list_tasks`
- `get_task`
- `create_task`
- `update_task`
- `add_comment`
- `search_tasks`
