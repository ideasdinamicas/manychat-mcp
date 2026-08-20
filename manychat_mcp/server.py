"""
ManyChat MCP Server — Multi-account
Reads accounts from individual env vars: MANYCHAT_<ALIAS>=api_key
Example: MANYCHAT_IQG=127881..., MANYCHAT_FUNDUP=abc123...
"""
import os, json, asyncio, httpx
from typing import Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

BASE_URL = "https://api.manychat.com"

def load_accounts() -> dict[str, str]:
    """
    Reads one env var per account: MANYCHAT_<ALIAS>=api_key
    Alias is whatever comes after MANYCHAT_ (e.g. IQG, FUNDUP, STORE2).
    Falls back to legacy MANYCHAT_ACCOUNTS JSON for backwards compatibility.
    """
    accounts = {}
    for key, val in os.environ.items():
        if key.startswith("MANYCHAT_") and key not in ("MANYCHAT_ACCOUNTS",) and val:
            alias = key[len("MANYCHAT_"):]
            accounts[alias] = val
    if not accounts:
        raw = os.environ.get("MANYCHAT_ACCOUNTS", "")
        if raw:
            try:
                accounts = json.loads(raw)
            except Exception:
                pass
    return accounts

ACCOUNTS = load_accounts()

async def mc_get(account: str, path: str, params: dict = None) -> dict:
    key = ACCOUNTS.get(account)
    if not key:
        return {"error": f"Account '{account}' not found. Available: {list(ACCOUNTS.keys())}"}
    async with httpx.AsyncClient() as c:
        r = await c.get(f"{BASE_URL}{path}", headers={"Authorization": f"Bearer {key}"}, params=params or {}, timeout=30)
        return r.json()

async def mc_post(account: str, path: str, body: dict = None) -> dict:
    key = ACCOUNTS.get(account)
    if not key:
        return {"error": f"Account '{account}' not found. Available: {list(ACCOUNTS.keys())}"}
    async with httpx.AsyncClient() as c:
        r = await c.post(f"{BASE_URL}{path}", headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"}, json=body or {}, timeout=30)
        return r.json()

def ok(result: Any) -> list[types.TextContent]:
    return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

server = Server("manychat-mcp")

@server.list_tools()
async def list_tools() -> list[types.Tool]:
    accs = str(list(ACCOUNTS.keys()))
    acc_prop = {"account": {"type": "string", "description": f"Account alias. Available: {accs}"}}

    def t(name, desc, props, req):
        return types.Tool(name=name, description=desc, inputSchema={"type": "object", "properties": props, "required": req})

    a = {"account": {"type": "string"}}

    return [
        t("list_accounts", "List configured ManyChat accounts.", {}, []),

        # Page
        t("page_get_info",             "Get page/bot info.",               acc_prop, ["account"]),
        t("page_get_tags",             "List all tags.",                   a, ["account"]),
        t("page_create_tag",           "Create a tag.",                    {**a, "name": {"type": "string"}}, ["account", "name"]),
        t("page_remove_tag",           "Delete a tag by ID.",              {**a, "tag_id": {"type": "integer"}}, ["account", "tag_id"]),
        t("page_get_custom_fields",    "List custom fields.",              a, ["account"]),
        t("page_create_custom_field",  "Create a custom field.",           {**a, "name": {"type": "string"}, "type": {"type": "string", "enum": ["text","number","date","datetime","boolean"]}, "description": {"type": "string"}}, ["account", "name", "type"]),
        t("page_get_flows",            "List all flows/automations.",      a, ["account"]),
        t("page_get_widgets",          "List widgets.",                    a, ["account"]),
        t("page_get_growth_tools",     "List growth tools.",               a, ["account"]),
        t("page_get_otn_topics",       "List OTN topics.",                 a, ["account"]),
        t("page_get_bot_fields",       "List bot fields.",                 a, ["account"]),
        t("page_create_bot_field",     "Create a bot field.",              {**a, "name": {"type": "string"}, "type": {"type": "string", "enum": ["text","number","date","datetime","boolean"]}, "description": {"type": "string"}}, ["account", "name", "type"]),
        t("page_set_bot_field",        "Set bot field value by ID.",       {**a, "field_id": {"type": "integer"}, "field_value": {"type": "string"}}, ["account", "field_id", "field_value"]),
        t("page_set_bot_field_by_name","Set bot field value by name.",     {**a, "field_name": {"type": "string"}, "field_value": {"type": "string"}}, ["account", "field_name", "field_value"]),

        # Subscriber
        t("subscriber_get_info",              "Get full subscriber info.",              {**a, "subscriber_id": {"type": "integer"}}, ["account", "subscriber_id"]),
        t("subscriber_find_by_name",          "Find subscribers by name.",              {**a, "name": {"type": "string"}}, ["account", "name"]),
        t("subscriber_find_by_custom_field",  "Find by custom field value.",            {**a, "field_id": {"type": "integer"}, "field_value": {"type": "string"}}, ["account", "field_id", "field_value"]),
        t("subscriber_find_by_system_field",  "Find by system field (email, phone).",   {**a, "field_name": {"type": "string"}, "field_value": {"type": "string"}}, ["account", "field_name", "field_value"]),
        t("subscriber_create",                "Create a new subscriber.",               {**a, "first_name": {"type": "string"}, "last_name": {"type": "string"}, "phone": {"type": "string"}, "email": {"type": "string"}, "gender": {"type": "string", "enum": ["male","female"]}, "has_opt_in_sms": {"type": "boolean"}, "has_opt_in_email": {"type": "boolean"}}, ["account"]),
        t("subscriber_update",                "Update subscriber data.",                {**a, "subscriber_id": {"type": "integer"}, "first_name": {"type": "string"}, "last_name": {"type": "string"}, "phone": {"type": "string"}, "email": {"type": "string"}, "has_opt_in_sms": {"type": "boolean"}, "has_opt_in_email": {"type": "boolean"}}, ["account", "subscriber_id"]),
        t("subscriber_add_tag",               "Add tag by ID.",                         {**a, "subscriber_id": {"type": "integer"}, "tag_id": {"type": "integer"}}, ["account", "subscriber_id", "tag_id"]),
        t("subscriber_add_tag_by_name",       "Add tag by name.",                       {**a, "subscriber_id": {"type": "integer"}, "tag_name": {"type": "string"}}, ["account", "subscriber_id", "tag_name"]),
        t("subscriber_remove_tag",            "Remove tag by ID.",                      {**a, "subscriber_id": {"type": "integer"}, "tag_id": {"type": "integer"}}, ["account", "subscriber_id", "tag_id"]),
        t("subscriber_remove_tag_by_name",    "Remove tag by name.",                    {**a, "subscriber_id": {"type": "integer"}, "tag_name": {"type": "string"}}, ["account", "subscriber_id", "tag_name"]),
        t("subscriber_set_custom_field",      "Set custom field by ID.",                {**a, "subscriber_id": {"type": "integer"}, "field_id": {"type": "integer"}, "field_value": {"type": "string"}}, ["account", "subscriber_id", "field_id", "field_value"]),
        t("subscriber_set_custom_field_by_name","Set custom field by name.",            {**a, "subscriber_id": {"type": "integer"}, "field_name": {"type": "string"}, "field_value": {"type": "string"}}, ["account", "subscriber_id", "field_name", "field_value"]),
        t("subscriber_set_custom_fields",     "Set multiple custom fields at once.",    {**a, "subscriber_id": {"type": "integer"}, "fields": {"type": "array", "items": {"type": "object", "properties": {"field_id": {"type": "integer"}, "field_value": {"type": "string"}}, "required": ["field_id", "field_value"]}}}, ["account", "subscriber_id", "fields"]),

        # Sending
        t("send_flow",    "Trigger a flow to a subscriber.",                     {**a, "subscriber_id": {"type": "integer"}, "flow_ns": {"type": "string", "description": "Flow namespace from page_get_flows"}}, ["account", "subscriber_id", "flow_ns"]),
        t("send_content", "Send custom content (text, image) to a subscriber.",  {**a, "subscriber_id": {"type": "integer"}, "message_tag": {"type": "string", "enum": ["ACCOUNT_UPDATE","POST_PURCHASE_UPDATE","CONFIRMED_EVENT_UPDATE","NON_PROMOTIONAL_SUBSCRIPTION"]}, "messages": {"type": "array", "items": {"type": "object"}}}, ["account", "subscriber_id", "message_tag", "messages"]),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    acc = arguments.get("account", "default")

    match name:
        case "list_accounts":                    return ok({"accounts": list(ACCOUNTS.keys())})
        case "page_get_info":                    return ok(await mc_get(acc, "/fb/page/getInfo"))
        case "page_get_tags":                    return ok(await mc_get(acc, "/fb/page/getTags"))
        case "page_create_tag":                  return ok(await mc_post(acc, "/fb/page/createTag", {"name": arguments["name"]}))
        case "page_remove_tag":                  return ok(await mc_post(acc, "/fb/page/removeTag", {"tag_id": arguments["tag_id"]}))
        case "page_get_custom_fields":           return ok(await mc_get(acc, "/fb/page/getCustomFields"))
        case "page_create_custom_field":
            b = {"name": arguments["name"], "type": arguments["type"]}
            if "description" in arguments: b["description"] = arguments["description"]
            return ok(await mc_post(acc, "/fb/page/createCustomField", b))
        case "page_get_flows":                   return ok(await mc_get(acc, "/fb/page/getFlows"))
        case "page_get_widgets":                 return ok(await mc_get(acc, "/fb/page/getWidgets"))
        case "page_get_growth_tools":            return ok(await mc_get(acc, "/fb/page/getGrowthTools"))
        case "page_get_otn_topics":              return ok(await mc_get(acc, "/fb/page/getOtnTopics"))
        case "page_get_bot_fields":              return ok(await mc_get(acc, "/fb/page/getBotFields"))
        case "page_create_bot_field":
            b = {"name": arguments["name"], "type": arguments["type"]}
            if "description" in arguments: b["description"] = arguments["description"]
            return ok(await mc_post(acc, "/fb/page/createBotField", b))
        case "page_set_bot_field":               return ok(await mc_post(acc, "/fb/page/setBotField", {"field_id": arguments["field_id"], "field_value": arguments["field_value"]}))
        case "page_set_bot_field_by_name":       return ok(await mc_post(acc, "/fb/page/setBotFieldByName", {"field_name": arguments["field_name"], "field_value": arguments["field_value"]}))
        case "subscriber_get_info":              return ok(await mc_get(acc, "/fb/subscriber/getInfo", {"subscriber_id": arguments["subscriber_id"]}))
        case "subscriber_find_by_name":          return ok(await mc_get(acc, "/fb/subscriber/findByName", {"name": arguments["name"]}))
        case "subscriber_find_by_custom_field":  return ok(await mc_get(acc, "/fb/subscriber/findByCustomField", {"field_id": arguments["field_id"], "field_value": arguments["field_value"]}))
        case "subscriber_find_by_system_field":  return ok(await mc_get(acc, "/fb/subscriber/findBySystemField", {"field_name": arguments["field_name"], "field_value": arguments["field_value"]}))
        case "subscriber_create":                return ok(await mc_post(acc, "/fb/subscriber/createSubscriber", {k: v for k, v in arguments.items() if k != "account"}))
        case "subscriber_update":                return ok(await mc_post(acc, "/fb/subscriber/updateSubscriber", {k: v for k, v in arguments.items() if k != "account"}))
        case "subscriber_add_tag":               return ok(await mc_post(acc, "/fb/subscriber/addTag", {"subscriber_id": arguments["subscriber_id"], "tag_id": arguments["tag_id"]}))
        case "subscriber_add_tag_by_name":       return ok(await mc_post(acc, "/fb/subscriber/addTagByName", {"subscriber_id": arguments["subscriber_id"], "tag_name": arguments["tag_name"]}))
        case "subscriber_remove_tag":            return ok(await mc_post(acc, "/fb/subscriber/removeTag", {"subscriber_id": arguments["subscriber_id"], "tag_id": arguments["tag_id"]}))
        case "subscriber_remove_tag_by_name":    return ok(await mc_post(acc, "/fb/subscriber/removeTagByName", {"subscriber_id": arguments["subscriber_id"], "tag_name": arguments["tag_name"]}))
        case "subscriber_set_custom_field":      return ok(await mc_post(acc, "/fb/subscriber/setCustomField", {"subscriber_id": arguments["subscriber_id"], "field_id": arguments["field_id"], "field_value": arguments["field_value"]}))
        case "subscriber_set_custom_field_by_name": return ok(await mc_post(acc, "/fb/subscriber/setCustomFieldByName", {"subscriber_id": arguments["subscriber_id"], "field_name": arguments["field_name"], "field_value": arguments["field_value"]}))
        case "subscriber_set_custom_fields":     return ok(await mc_post(acc, "/fb/subscriber/setCustomFields", {"subscriber_id": arguments["subscriber_id"], "fields": arguments["fields"]}))
        case "send_flow":                        return ok(await mc_post(acc, "/fb/sending/sendFlow", {"subscriber_id": arguments["subscriber_id"], "flow_ns": arguments["flow_ns"]}))
        case "send_content":                     return ok(await mc_post(acc, "/fb/sending/sendContent", {"subscriber_id": arguments["subscriber_id"], "data": {"version": "v2", "content": {"messages": arguments["messages"], "message_tag": arguments["message_tag"]}}}))
        case _:                                  return ok({"error": f"Tool '{name}' not implemented."})


async def main():
    async with stdio_server() as (r, w):
        await server.run(r, w, server.create_initialization_options())

def main_sync():
    asyncio.run(main())

if __name__ == "__main__":
    main_sync()
