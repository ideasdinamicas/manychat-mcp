"""
ManyChat MCP Server
Expone toda la API pública de ManyChat como herramientas MCP.
Multi-cuenta: configura múltiples API keys en el archivo de config o env vars.
"""

import os
import json
import httpx
from typing import Any, Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

# ── Config ────────────────────────────────────────────────────────────────────
# Carga cuentas desde variables de entorno:
# MANYCHAT_ACCOUNTS=json con {alias: api_key} 
# Ejemplo: {"IQG": "127881...", "OtraCuenta": "abc123..."}
# O simplemente MANYCHAT_API_KEY para una sola cuenta

BASE_URL = "https://api.manychat.com"

def load_accounts() -> dict[str, str]:
    raw = os.environ.get("MANYCHAT_ACCOUNTS")
    if raw:
        try:
            return json.loads(raw)
        except Exception:
            pass
    single = os.environ.get("MANYCHAT_API_KEY")
    if single:
        return {"default": single}
    return {}

ACCOUNTS = load_accounts()

# ── HTTP helper ───────────────────────────────────────────────────────────────

async def mc_get(account: str, path: str, params: dict = None) -> dict:
    api_key = ACCOUNTS.get(account)
    if not api_key:
        return {"error": f"Account '{account}' not found. Available: {list(ACCOUNTS.keys())}"}
    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{BASE_URL}{path}",
            headers={"Authorization": f"Bearer {api_key}"},
            params=params or {},
            timeout=30,
        )
        return r.json()

async def mc_post(account: str, path: str, body: dict = None) -> dict:
    api_key = ACCOUNTS.get(account)
    if not api_key:
        return {"error": f"Account '{account}' not found. Available: {list(ACCOUNTS.keys())}"}
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{BASE_URL}{path}",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=body or {},
            timeout=30,
        )
        return r.json()

def ok(result: Any) -> list[types.TextContent]:
    return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

def accounts_list() -> str:
    return str(list(ACCOUNTS.keys()))

# ── Server ────────────────────────────────────────────────────────────────────

server = Server("manychat-mcp")

@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [

        # ── META / ACCOUNTS ────────────────────────────────────────────────
        types.Tool(
            name="list_accounts",
            description="Lista las cuentas ManyChat configuradas (aliases disponibles para el parámetro 'account').",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),

        # ── PAGE ───────────────────────────────────────────────────────────
        types.Tool(
            name="page_get_info",
            description="Obtiene información de la página/bot de ManyChat.",
            inputSchema={
                "type": "object",
                "properties": {"account": {"type": "string", "description": f"Alias de cuenta. Disponibles: {accounts_list()}"}},
                "required": ["account"],
            },
        ),
        types.Tool(
            name="page_get_tags",
            description="Lista todos los tags de la página.",
            inputSchema={
                "type": "object",
                "properties": {"account": {"type": "string"}},
                "required": ["account"],
            },
        ),
        types.Tool(
            name="page_create_tag",
            description="Crea un nuevo tag en la página.",
            inputSchema={
                "type": "object",
                "properties": {
                    "account": {"type": "string"},
                    "name": {"type": "string", "description": "Nombre del tag"},
                },
                "required": ["account", "name"],
            },
        ),
        types.Tool(
            name="page_remove_tag",
            description="Elimina un tag de la página por ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "account": {"type": "string"},
                    "tag_id": {"type": "integer", "description": "ID del tag a eliminar"},
                },
                "required": ["account", "tag_id"],
            },
        ),
        types.Tool(
            name="page_get_custom_fields",
            description="Lista todos los campos personalizados de la página.",
            inputSchema={
                "type": "object",
                "properties": {"account": {"type": "string"}},
                "required": ["account"],
            },
        ),
        types.Tool(
            name="page_create_custom_field",
            description="Crea un campo personalizado en la página.",
            inputSchema={
                "type": "object",
                "properties": {
                    "account": {"type": "string"},
                    "name": {"type": "string"},
                    "type": {"type": "string", "enum": ["text", "number", "date", "datetime", "boolean"], "description": "Tipo del campo"},
                    "description": {"type": "string", "description": "Descripción opcional"},
                },
                "required": ["account", "name", "type"],
            },
        ),
        types.Tool(
            name="page_get_flows",
            description="Lista todos los flujos/automatizaciones de la página.",
            inputSchema={
                "type": "object",
                "properties": {"account": {"type": "string"}},
                "required": ["account"],
            },
        ),
        types.Tool(
            name="page_get_widgets",
            description="Lista los widgets (growth tools) de la página.",
            inputSchema={
                "type": "object",
                "properties": {"account": {"type": "string"}},
                "required": ["account"],
            },
        ),
        types.Tool(
            name="page_get_growth_tools",
            description="Lista los growth tools de la página.",
            inputSchema={
                "type": "object",
                "properties": {"account": {"type": "string"}},
                "required": ["account"],
            },
        ),
        types.Tool(
            name="page_get_otn_topics",
            description="Lista los temas OTN (One-Time Notification) de la página.",
            inputSchema={
                "type": "object",
                "properties": {"account": {"type": "string"}},
                "required": ["account"],
            },
        ),
        types.Tool(
            name="page_get_bot_fields",
            description="Lista los campos de bot (bot-level variables) de la página.",
            inputSchema={
                "type": "object",
                "properties": {"account": {"type": "string"}},
                "required": ["account"],
            },
        ),
        types.Tool(
            name="page_create_bot_field",
            description="Crea un campo de bot.",
            inputSchema={
                "type": "object",
                "properties": {
                    "account": {"type": "string"},
                    "name": {"type": "string"},
                    "type": {"type": "string", "enum": ["text", "number", "date", "datetime", "boolean"]},
                    "description": {"type": "string"},
                },
                "required": ["account", "name", "type"],
            },
        ),
        types.Tool(
            name="page_set_bot_field",
            description="Establece el valor de un campo de bot por ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "account": {"type": "string"},
                    "field_id": {"type": "integer"},
                    "field_value": {"type": "string", "description": "Valor a establecer"},
                },
                "required": ["account", "field_id", "field_value"],
            },
        ),
        types.Tool(
            name="page_set_bot_field_by_name",
            description="Establece el valor de un campo de bot por nombre.",
            inputSchema={
                "type": "object",
                "properties": {
                    "account": {"type": "string"},
                    "field_name": {"type": "string"},
                    "field_value": {"type": "string"},
                },
                "required": ["account", "field_name", "field_value"],
            },
        ),

        # ── SUBSCRIBER ─────────────────────────────────────────────────────
        types.Tool(
            name="subscriber_get_info",
            description="Obtiene información completa de un suscriptor por su ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "account": {"type": "string"},
                    "subscriber_id": {"type": "integer", "description": "ID del suscriptor"},
                },
                "required": ["account", "subscriber_id"],
            },
        ),
        types.Tool(
            name="subscriber_find_by_name",
            description="Busca suscriptores por nombre.",
            inputSchema={
                "type": "object",
                "properties": {
                    "account": {"type": "string"},
                    "name": {"type": "string", "description": "Nombre a buscar"},
                },
                "required": ["account", "name"],
            },
        ),
        types.Tool(
            name="subscriber_find_by_custom_field",
            description="Busca suscriptores por valor de campo personalizado.",
            inputSchema={
                "type": "object",
                "properties": {
                    "account": {"type": "string"},
                    "field_id": {"type": "integer"},
                    "field_value": {"type": "string"},
                },
                "required": ["account", "field_id", "field_value"],
            },
        ),
        types.Tool(
            name="subscriber_find_by_system_field",
            description="Busca suscriptores por campo de sistema (email, phone, etc.).",
            inputSchema={
                "type": "object",
                "properties": {
                    "account": {"type": "string"},
                    "field_name": {"type": "string", "description": "Nombre del campo sistema (e.g. 'email', 'phone')"},
                    "field_value": {"type": "string"},
                },
                "required": ["account", "field_name", "field_value"],
            },
        ),
        types.Tool(
            name="subscriber_create",
            description="Crea un nuevo suscriptor en ManyChat.",
            inputSchema={
                "type": "object",
                "properties": {
                    "account": {"type": "string"},
                    "first_name": {"type": "string"},
                    "last_name": {"type": "string"},
                    "phone": {"type": "string"},
                    "email": {"type": "string"},
                    "gender": {"type": "string", "enum": ["male", "female"]},
                    "has_opt_in_sms": {"type": "boolean"},
                    "has_opt_in_email": {"type": "boolean"},
                    "consent_phrase": {"type": "string"},
                },
                "required": ["account"],
            },
        ),
        types.Tool(
            name="subscriber_update",
            description="Actualiza datos de un suscriptor existente.",
            inputSchema={
                "type": "object",
                "properties": {
                    "account": {"type": "string"},
                    "subscriber_id": {"type": "integer"},
                    "first_name": {"type": "string"},
                    "last_name": {"type": "string"},
                    "phone": {"type": "string"},
                    "email": {"type": "string"},
                    "has_opt_in_sms": {"type": "boolean"},
                    "has_opt_in_email": {"type": "boolean"},
                },
                "required": ["account", "subscriber_id"],
            },
        ),
        types.Tool(
            name="subscriber_add_tag",
            description="Agrega un tag a un suscriptor por ID de tag.",
            inputSchema={
                "type": "object",
                "properties": {
                    "account": {"type": "string"},
                    "subscriber_id": {"type": "integer"},
                    "tag_id": {"type": "integer"},
                },
                "required": ["account", "subscriber_id", "tag_id"],
            },
        ),
        types.Tool(
            name="subscriber_add_tag_by_name",
            description="Agrega un tag a un suscriptor por nombre de tag.",
            inputSchema={
                "type": "object",
                "properties": {
                    "account": {"type": "string"},
                    "subscriber_id": {"type": "integer"},
                    "tag_name": {"type": "string"},
                },
                "required": ["account", "subscriber_id", "tag_name"],
            },
        ),
        types.Tool(
            name="subscriber_remove_tag",
            description="Remueve un tag de un suscriptor por ID de tag.",
            inputSchema={
                "type": "object",
                "properties": {
                    "account": {"type": "string"},
                    "subscriber_id": {"type": "integer"},
                    "tag_id": {"type": "integer"},
                },
                "required": ["account", "subscriber_id", "tag_id"],
            },
        ),
        types.Tool(
            name="subscriber_remove_tag_by_name",
            description="Remueve un tag de un suscriptor por nombre.",
            inputSchema={
                "type": "object",
                "properties": {
                    "account": {"type": "string"},
                    "subscriber_id": {"type": "integer"},
                    "tag_name": {"type": "string"},
                },
                "required": ["account", "subscriber_id", "tag_name"],
            },
        ),
        types.Tool(
            name="subscriber_set_custom_field",
            description="Establece un campo personalizado en un suscriptor por ID de campo.",
            inputSchema={
                "type": "object",
                "properties": {
                    "account": {"type": "string"},
                    "subscriber_id": {"type": "integer"},
                    "field_id": {"type": "integer"},
                    "field_value": {"type": "string"},
                },
                "required": ["account", "subscriber_id", "field_id", "field_value"],
            },
        ),
        types.Tool(
            name="subscriber_set_custom_field_by_name",
            description="Establece un campo personalizado en un suscriptor por nombre de campo.",
            inputSchema={
                "type": "object",
                "properties": {
                    "account": {"type": "string"},
                    "subscriber_id": {"type": "integer"},
                    "field_name": {"type": "string"},
                    "field_value": {"type": "string"},
                },
                "required": ["account", "subscriber_id", "field_name", "field_value"],
            },
        ),
        types.Tool(
            name="subscriber_set_custom_fields",
            description="Establece múltiples campos personalizados en un suscriptor de una vez.",
            inputSchema={
                "type": "object",
                "properties": {
                    "account": {"type": "string"},
                    "subscriber_id": {"type": "integer"},
                    "fields": {
                        "type": "array",
                        "description": "Lista de campos a actualizar",
                        "items": {
                            "type": "object",
                            "properties": {
                                "field_id": {"type": "integer"},
                                "field_value": {"type": "string"},
                            },
                            "required": ["field_id", "field_value"],
                        },
                    },
                },
                "required": ["account", "subscriber_id", "fields"],
            },
        ),

        # ── SENDING ────────────────────────────────────────────────────────
        types.Tool(
            name="send_flow",
            description="Envía un flujo/automatización a un suscriptor.",
            inputSchema={
                "type": "object",
                "properties": {
                    "account": {"type": "string"},
                    "subscriber_id": {"type": "integer"},
                    "flow_ns": {"type": "string", "description": "Namespace del flujo (obtenlo con page_get_flows)"},
                },
                "required": ["account", "subscriber_id", "flow_ns"],
            },
        ),
        types.Tool(
            name="send_content",
            description="Envía contenido personalizado (texto, imagen, etc.) a un suscriptor vía Messenger.",
            inputSchema={
                "type": "object",
                "properties": {
                    "account": {"type": "string"},
                    "subscriber_id": {"type": "integer"},
                    "message_tag": {
                        "type": "string",
                        "enum": ["ACCOUNT_UPDATE", "POST_PURCHASE_UPDATE", "CONFIRMED_EVENT_UPDATE", "NON_PROMOTIONAL_SUBSCRIPTION"],
                        "description": "Tag de mensaje requerido por Meta",
                    },
                    "messages": {
                        "type": "array",
                        "description": "Array de mensajes a enviar",
                        "items": {"type": "object"},
                    },
                    "notification_messages_timezone": {"type": "string", "description": "Timezone para notificaciones"},
                },
                "required": ["account", "subscriber_id", "message_tag", "messages"],
            },
        ),

    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    acc = arguments.get("account", "default")

    # ── META ──────────────────────────────────────────────────────────────
    if name == "list_accounts":
        return ok({"accounts": list(ACCOUNTS.keys()), "count": len(ACCOUNTS)})

    # ── PAGE ──────────────────────────────────────────────────────────────
    elif name == "page_get_info":
        return ok(await mc_get(acc, "/fb/page/getInfo"))

    elif name == "page_get_tags":
        return ok(await mc_get(acc, "/fb/page/getTags"))

    elif name == "page_create_tag":
        return ok(await mc_post(acc, "/fb/page/createTag", {"name": arguments["name"]}))

    elif name == "page_remove_tag":
        return ok(await mc_post(acc, "/fb/page/removeTag", {"tag_id": arguments["tag_id"]}))

    elif name == "page_get_custom_fields":
        return ok(await mc_get(acc, "/fb/page/getCustomFields"))

    elif name == "page_create_custom_field":
        body = {"name": arguments["name"], "type": arguments["type"]}
        if "description" in arguments:
            body["description"] = arguments["description"]
        return ok(await mc_post(acc, "/fb/page/createCustomField", body))

    elif name == "page_get_flows":
        return ok(await mc_get(acc, "/fb/page/getFlows"))

    elif name == "page_get_widgets":
        return ok(await mc_get(acc, "/fb/page/getWidgets"))

    elif name == "page_get_growth_tools":
        return ok(await mc_get(acc, "/fb/page/getGrowthTools"))

    elif name == "page_get_otn_topics":
        return ok(await mc_get(acc, "/fb/page/getOtnTopics"))

    elif name == "page_get_bot_fields":
        return ok(await mc_get(acc, "/fb/page/getBotFields"))

    elif name == "page_create_bot_field":
        body = {"name": arguments["name"], "type": arguments["type"]}
        if "description" in arguments:
            body["description"] = arguments["description"]
        return ok(await mc_post(acc, "/fb/page/createBotField", body))

    elif name == "page_set_bot_field":
        return ok(await mc_post(acc, "/fb/page/setBotField", {
            "field_id": arguments["field_id"],
            "field_value": arguments["field_value"],
        }))

    elif name == "page_set_bot_field_by_name":
        return ok(await mc_post(acc, "/fb/page/setBotFieldByName", {
            "field_name": arguments["field_name"],
            "field_value": arguments["field_value"],
        }))

    # ── SUBSCRIBER ────────────────────────────────────────────────────────
    elif name == "subscriber_get_info":
        return ok(await mc_get(acc, "/fb/subscriber/getInfo", {"subscriber_id": arguments["subscriber_id"]}))

    elif name == "subscriber_find_by_name":
        return ok(await mc_get(acc, "/fb/subscriber/findByName", {"name": arguments["name"]}))

    elif name == "subscriber_find_by_custom_field":
        return ok(await mc_get(acc, "/fb/subscriber/findByCustomField", {
            "field_id": arguments["field_id"],
            "field_value": arguments["field_value"],
        }))

    elif name == "subscriber_find_by_system_field":
        return ok(await mc_get(acc, "/fb/subscriber/findBySystemField", {
            "field_name": arguments["field_name"],
            "field_value": arguments["field_value"],
        }))

    elif name == "subscriber_create":
        body = {k: v for k, v in arguments.items() if k != "account"}
        return ok(await mc_post(acc, "/fb/subscriber/createSubscriber", body))

    elif name == "subscriber_update":
        body = {k: v for k, v in arguments.items() if k not in ("account",)}
        return ok(await mc_post(acc, "/fb/subscriber/updateSubscriber", body))

    elif name == "subscriber_add_tag":
        return ok(await mc_post(acc, "/fb/subscriber/addTag", {
            "subscriber_id": arguments["subscriber_id"],
            "tag_id": arguments["tag_id"],
        }))

    elif name == "subscriber_add_tag_by_name":
        return ok(await mc_post(acc, "/fb/subscriber/addTagByName", {
            "subscriber_id": arguments["subscriber_id"],
            "tag_name": arguments["tag_name"],
        }))

    elif name == "subscriber_remove_tag":
        return ok(await mc_post(acc, "/fb/subscriber/removeTag", {
            "subscriber_id": arguments["subscriber_id"],
            "tag_id": arguments["tag_id"],
        }))

    elif name == "subscriber_remove_tag_by_name":
        return ok(await mc_post(acc, "/fb/subscriber/removeTagByName", {
            "subscriber_id": arguments["subscriber_id"],
            "tag_name": arguments["tag_name"],
        }))

    elif name == "subscriber_set_custom_field":
        return ok(await mc_post(acc, "/fb/subscriber/setCustomField", {
            "subscriber_id": arguments["subscriber_id"],
            "field_id": arguments["field_id"],
            "field_value": arguments["field_value"],
        }))

    elif name == "subscriber_set_custom_field_by_name":
        return ok(await mc_post(acc, "/fb/subscriber/setCustomFieldByName", {
            "subscriber_id": arguments["subscriber_id"],
            "field_name": arguments["field_name"],
            "field_value": arguments["field_value"],
        }))

    elif name == "subscriber_set_custom_fields":
        return ok(await mc_post(acc, "/fb/subscriber/setCustomFields", {
            "subscriber_id": arguments["subscriber_id"],
            "fields": arguments["fields"],
        }))

    # ── SENDING ───────────────────────────────────────────────────────────
    elif name == "send_flow":
        return ok(await mc_post(acc, "/fb/sending/sendFlow", {
            "subscriber_id": arguments["subscriber_id"],
            "flow_ns": arguments["flow_ns"],
        }))

    elif name == "send_content":
        body = {
            "subscriber_id": arguments["subscriber_id"],
            "data": {
                "version": "v2",
                "content": {
                    "messages": arguments["messages"],
                    "message_tag": arguments["message_tag"],
                },
            },
        }
        return ok(await mc_post(acc, "/fb/sending/sendContent", body))

    else:
        return ok({"error": f"Tool '{name}' not implemented."})


# ── Entry point ───────────────────────────────────────────────────────────────

async def main():
    async with stdio_server() as streams:
        await server.run(streams[0], streams[1], server.create_initialization_options())

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
