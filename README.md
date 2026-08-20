# ManyChat MCP Server

MCP Server that exposes the full ManyChat public API as tools for Claude Desktop, Cursor, or any MCP-compatible client.

**29 tools** — subscribers, tags, custom fields, bot fields, flows, growth tools, sending.  
**Multi-account** — one env var per page, no JSON escaping hell.

---

## Setup (Claude Desktop)

### Step 1 — Edit `claude_desktop_config.json`

| OS | File location |
|----|--------------|
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Linux | `~/.config/Claude/claude_desktop_config.json` |

```json
{
  "mcpServers": {
    "manychat": {
      "command": "uvx",
      "args": [
        "--from", "git+https://github.com/ideasdinamicas/manychat-mcp",
        "manychat-mcp"
      ],
      "env": {
        "MANYCHAT_IQG": "your_iqg_api_key_here"
      }
    }
  }
}
```

### Step 2 — Restart Claude Desktop

That's it. `uvx` downloads and runs the server automatically — no manual install needed.

---

## Multi-account

Add one env var per account using the pattern `MANYCHAT_<ALIAS>`:

```json
{
  "mcpServers": {
    "manychat": {
      "command": "uvx",
      "args": [
        "--from", "git+https://github.com/ideasdinamicas/manychat-mcp",
        "manychat-mcp"
      ],
      "env": {
        "MANYCHAT_IQG":    "api_key_for_iqg",
        "MANYCHAT_FUNDUP": "api_key_for_fundup",
        "MANYCHAT_ESCUELA": "api_key_for_escuela"
      }
    }
  }
}
```

Each tool receives an `account` parameter where you pass the alias (`"IQG"`, `"FUNDUP"`, etc.).

---

## Prerequisites

- **uvx** (comes with `uv`) — [install uv](https://docs.astral.sh/uv/getting-started/installation/)
  ```bash
  # Windows (PowerShell)
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  
  # macOS / Linux
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

---

## Getting your ManyChat API key

1. Go to ManyChat → **Settings → API**
2. Generate an access token

---

## Available tools

| Category | Tool | Description |
|----------|------|-------------|
| Meta | `list_accounts` | List configured accounts |
| Page | `page_get_info` | Get page/bot info |
| Page | `page_get_tags` | List all tags |
| Page | `page_create_tag` | Create a tag |
| Page | `page_remove_tag` | Delete a tag by ID |
| Page | `page_get_custom_fields` | List custom fields |
| Page | `page_create_custom_field` | Create a custom field |
| Page | `page_get_flows` | List all flows/automations |
| Page | `page_get_widgets` | List widgets |
| Page | `page_get_growth_tools` | List growth tools |
| Page | `page_get_otn_topics` | List OTN topics |
| Page | `page_get_bot_fields` | List bot fields |
| Page | `page_create_bot_field` | Create a bot field |
| Page | `page_set_bot_field` | Set bot field value by ID |
| Page | `page_set_bot_field_by_name` | Set bot field value by name |
| Subscriber | `subscriber_get_info` | Get full subscriber info |
| Subscriber | `subscriber_find_by_name` | Search by name |
| Subscriber | `subscriber_find_by_custom_field` | Search by custom field |
| Subscriber | `subscriber_find_by_system_field` | Search by email/phone |
| Subscriber | `subscriber_create` | Create a new subscriber |
| Subscriber | `subscriber_update` | Update subscriber data |
| Subscriber | `subscriber_add_tag` | Add tag by ID |
| Subscriber | `subscriber_add_tag_by_name` | Add tag by name |
| Subscriber | `subscriber_remove_tag` | Remove tag by ID |
| Subscriber | `subscriber_remove_tag_by_name` | Remove tag by name |
| Subscriber | `subscriber_set_custom_field` | Set custom field by ID |
| Subscriber | `subscriber_set_custom_field_by_name` | Set custom field by name |
| Subscriber | `subscriber_set_custom_fields` | Set multiple fields at once |
| Sending | `send_flow` | Trigger a flow to a subscriber |
| Sending | `send_content` | Send custom content to a subscriber |

---

## Limitations of the ManyChat API

The public API does **not** support creating/editing flows, managing broadcasts, or accessing analytics. Everything it does expose is covered here.
