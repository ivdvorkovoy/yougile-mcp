# YouGile MCP client config

The server is running on the Linux notebook at:

- `~/yougile-mcp-starter/.venv/bin/yougile-mcp`
- env file: `~/yougile-mcp-starter/.env`

## Generic MCP server entry

```json
{
  "mcpServers": {
    "yougile": {
      "command": "/home/general/yougile-mcp-starter/.venv/bin/yougile-mcp",
      "env": {
        "YOUGILE_DOTENV_PATH": "/home/general/yougile-mcp-starter/.env"
      }
    }
  }
}
```

## Notes

- If your client supports `envFile`, point it to `/home/general/yougile-mcp-starter/.env`.
- If it wants a shell command, use the absolute `yougile-mcp` path above.
- The server already stores the generated API key back into `.env` on first successful auth.

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

