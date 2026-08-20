# ManyChat MCP Server

MCP Server that exposes the full ManyChat public API as tools for Claude Desktop, Cursor, or any MCP-compatible client.

**29 tools** covering everything the ManyChat API supports:
- Page info, tags, custom fields, bot fields, flows, widgets, growth tools, OTN topics
- Subscriber management (create, update, find, tags, custom fields)
- Sending (trigger flows, send custom content)

**Multi-account** — configure as many ManyChat pages as you want.

---

## Installation (Windows)

### 1. Install Python dependencies

```powershell
pip install mcp httpx
```

### 2. Download the server

```powershell
mkdir "$env:USERPROFILE\Projects\manychat-mcp" -Force
cd "$env:USERPROFILE\Projects\manychat-mcp"
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/ideasdinamicas/manychat-mcp/main/server.py" -OutFile "server.py"
```

### 3. Configure Claude Desktop

Open (or create) this file:
```
%APPDATA%\Claude\claude_desktop_config.json
```

Add this configuration (replace `YOUR_MANYCHAT_API_KEY`):

```json
{
  "mcpServers": {
    "manychat": {
      "command": "python",
      "args": ["%USERPROFILE%\\Projects\\manychat-mcp\\server.py"],
      "env": {
        "MANYCHAT_ACCOUNTS": "{\"MyPage\": \"YOUR_MANYCHAT_API_KEY\"}"
      }
    }
  }
}
```

### 4. Restart Claude Desktop

Close and reopen Claude Desktop. You'll see the 🔧 icon with ManyChat tools available.

---

## Installation (macOS / Linux)

```bash
mkdir -p ~/Projects/manychat-mcp
cd ~/Projects/manychat-mcp
curl -O https://raw.githubusercontent.com/ideasdinamicas/manychat-mcp/main/server.py
pip install mcp httpx
```

Config file location:
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux:** `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "manychat": {
      "command": "python3",
      "args": ["/Users/YOUR_USER/Projects/manychat-mcp/server.py"],
      "env": {
        "MANYCHAT_ACCOUNTS": "{\"MyPage\": \"YOUR_MANYCHAT_API_KEY\"}"
      }
    }
  }
}
```

---

## Multi-account setup

`MANYCHAT_ACCOUNTS` is a JSON string with account aliases and their API keys:

```json
{
  "mcpServers": {
    "manychat": {
      "command": "python",
      "args": ["%USERPROFILE%\\Projects\\manychat-mcp\\server.py"],
      "env": {
        "MANYCHAT_ACCOUNTS": "{\"Store1\": \"key1\", \"Store2\": \"key2\", \"Agency\": \"key3\"}"
      }
    }
  }
}
```

Each tool receives an `account` parameter where you pass the alias (e.g. `"Store1"`).

---

## Getting your ManyChat API key

1. Go to ManyChat → **Settings → API**
2. Generate an access token
3. The format is `{page_id}:{token}`

---

## Available tools

| Tool | Description |
|------|-------------|
| `list_accounts` | List configured accounts |
| `page_get_info` | Get page/bot info |
| `page_get_tags` | List all tags |
| `page_create_tag` | Create a tag |
| `page_remove_tag` | Delete a tag |
| `page_get_custom_fields` | List custom fields |
| `page_create_custom_field` | Create a custom field |
| `page_get_flows` | List all flows/automations |
| `page_get_widgets` | List widgets |
| `page_get_growth_tools` | List growth tools |
| `page_get_otn_topics` | List OTN topics |
| `page_get_bot_fields` | List bot fields |
| `page_create_bot_field` | Create a bot field |
| `page_set_bot_field` | Set bot field value by ID |
| `page_set_bot_field_by_name` | Set bot field value by name |
| `subscriber_get_info` | Get subscriber details |
| `subscriber_find_by_name` | Search subscribers by name |
| `subscriber_find_by_custom_field` | Search by custom field |
| `subscriber_find_by_system_field` | Search by email/phone |
| `subscriber_create` | Create a new subscriber |
| `subscriber_update` | Update subscriber data |
| `subscriber_add_tag` | Add tag by ID |
| `subscriber_add_tag_by_name` | Add tag by name |
| `subscriber_remove_tag` | Remove tag by ID |
| `subscriber_remove_tag_by_name` | Remove tag by name |
| `subscriber_set_custom_field` | Set custom field by ID |
| `subscriber_set_custom_field_by_name` | Set custom field by name |
| `subscriber_set_custom_fields` | Set multiple custom fields at once |
| `send_flow` | Trigger a flow to a subscriber |
| `send_content` | Send custom content to a subscriber |

---

## Limitations

The ManyChat public API does **not** support:
- Creating or editing flows from scratch (use the UI for that)
- Managing broadcasts
- Detailed analytics/metrics

Everything the API does expose is covered by this server.
