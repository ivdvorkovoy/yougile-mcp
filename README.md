# yougile-mcp

Локальный MCP-сервер для YouGile. Он принимает команды от MCP-клиента и обращается **напрямую** к вашему YouGile по REST API.

## Зачем это нужно

- чтобы управлять YouGile из Claude, Codex, Continue, Cline и других MCP-клиентов;
- чтобы не зависеть от сторонних облачных прокладок;
- чтобы держать авторизацию и доступы у себя локально;
- чтобы собрать удобный мост между ИИ-агентом и рабочими задачами.

## Почему эта сборка удобнее и спокойнее

Главная идея простая: **данные не уходят в сторонние SaaS-сервисы**, а запросы идут прямо в ваш YouGile.

Это значит:

- нет промежуточного сервера между вами и YouGile;
- нет отдельного внешнего брокера для задач;
- секреты хранятся локально в `.env`;
- при желании сервер можно поднять на своём ноутбуке или внутренней машине;
- сетевой маршрут прозрачен: MCP-клиент -> локальный MCP-сервер -> YouGile.

Важно: это не магическая “сертификация безопасности”, а просто более короткий и понятный путь для данных. Итоговая безопасность всё равно зависит от того, где вы запускаете сервер и кому даёте доступ к `.env`.

## Что уже умеет сборка

### Базовые сущности

- проекты;
- доски;
- колонки;
- задачи;
- комментарии к задачам;
- поиск задач;
- сотрудники и пользователи;
- групповые чаты;
- сообщения в чатах;
- роли в проектах.
- отделы / departments;

### Стикеры

- sprint stickers;
- states для sprint stickers;
- string stickers;
- states для string stickers.

### Администрирование

- компании;
- API-ключи;
- удаление API-ключа.

## Как это работает

1. MCP-клиент запускает локальный сервер `yougile-mcp`.
2. Сервер читает настройки из `.env`.
3. Сервер получает API key, если он ещё не задан.
4. Сервер ходит в YouGile напрямую по REST API.
5. Результат возвращается обратно в MCP-клиент.

## Настройка

1. Скопируйте `.env.example` в `.env`.
2. Укажите `YOUGILE_BASE_URL`.
3. Задайте один из вариантов:
   - `YOUGILE_API_KEY`;
   - или `YOUGILE_EMAIL` + `YOUGILE_PASSWORD` + `YOUGILE_COMPANY_ID`.
4. Установите зависимости.
5. Запустите сервер как MCP-процесс.

## Переменные окружения

- `YOUGILE_BASE_URL` - адрес вашей установки YouGile;
- `YOUGILE_API_KEY` - готовый API key;
- `YOUGILE_EMAIL` - логин;
- `YOUGILE_PASSWORD` - пароль;
- `YOUGILE_COMPANY_ID` - id компании;
- `YOUGILE_COMPANY_NAME` - имя компании, если у вас их несколько;
- `YOUGILE_DOTENV_PATH` - путь до `.env`;
- `YOUGILE_TIMEOUT_SECONDS` - таймаут HTTP-запросов;
- `YOUGILE_RATE_LIMIT_PER_MINUTE` - лимит запросов в минуту.

## Доступные tools

### Проекты, доски и колонки

- `list_projects`
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

### Задачи и комментарии

- `list_tasks`
- `get_task`
- `create_task`
- `update_task`
- `add_comment`
- `search_tasks`
- `get_task_chat_subscribers`
- `update_task_chat_subscribers`

`create_task` и `update_task` поддерживают не только базовые поля, но и расширенные структуры задачи: подзадачи, чеклисты, стикеры, цвет, таймер, секундомер и time tracking.

### Сотрудники и чаты

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

### Роли и стикеры

- `list_project_roles`
- `create_project_role`
- `update_project_role`
- `delete_project_role`
- `list_departments`
- `get_department`
- `create_department`
- `update_department`
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
- `list_event_subscriptions`  (webhooks)
- `get_event_subscription`
- `create_event_subscription`
- `update_event_subscription`
- `delete_event_subscription`

### Админка

- `list_companies`
- `list_api_keys`
- `delete_api_key`

## Пример подключения

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

## Подсказка

Если хотите, чтобы сервер жил долго и стабильно, лучше запускать его:

- на своём ноутбуке;
- на внутренней Linux-машине;
- или на домашнем мини-сервере.

Тогда MCP-клиенты будут работать с ним как с обычным локальным инструментом, а доступ к YouGile останется у вас под контролем.
