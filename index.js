#!/usr/bin/env node
/**
 * ManyChat MCP Server
 * Multi-account via env vars: MANYCHAT_<ALIAS>=api_key
 * Example: MANYCHAT_IQG=127881..., MANYCHAT_FUNDUP=abc123...
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";

const BASE_URL = "https://api.manychat.com";

// Load accounts from MANYCHAT_<ALIAS>=key env vars
function loadAccounts() {
  const accounts = {};
  for (const [key, val] of Object.entries(process.env)) {
    if (key.startsWith("MANYCHAT_") && val) {
      const alias = key.slice("MANYCHAT_".length);
      accounts[alias] = val;
    }
  }
  return accounts;
}

const ACCOUNTS = loadAccounts();

async function mcGet(account, path, params = {}) {
  const key = ACCOUNTS[account];
  if (!key) return { error: `Account '${account}' not found. Available: ${Object.keys(ACCOUNTS).join(", ")}` };
  const url = new URL(`${BASE_URL}${path}`);
  Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v));
  const res = await fetch(url, { headers: { Authorization: `Bearer ${key}` } });
  return res.json();
}

async function mcPost(account, path, body = {}) {
  const key = ACCOUNTS[account];
  if (!key) return { error: `Account '${account}' not found. Available: ${Object.keys(ACCOUNTS).join(", ")}` };
  const res = await fetch(`${BASE_URL}${path}`, {
    method: "POST",
    headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return res.json();
}

function ok(result) {
  return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
}

// ── Tool definitions ──────────────────────────────────────────────────────────

const TOOLS = [
  // Meta
  { name: "list_accounts", description: "List configured ManyChat accounts.", inputSchema: { type: "object", properties: {}, required: [] } },

  // Page
  { name: "page_get_info",             description: "Get page/bot info.",                   inputSchema: { type: "object", properties: { account: { type: "string" } }, required: ["account"] } },
  { name: "page_get_tags",             description: "List all tags.",                        inputSchema: { type: "object", properties: { account: { type: "string" } }, required: ["account"] } },
  { name: "page_create_tag",           description: "Create a tag.",                         inputSchema: { type: "object", properties: { account: { type: "string" }, name: { type: "string" } }, required: ["account", "name"] } },
  { name: "page_remove_tag",           description: "Delete a tag by ID.",                   inputSchema: { type: "object", properties: { account: { type: "string" }, tag_id: { type: "integer" } }, required: ["account", "tag_id"] } },
  { name: "page_get_custom_fields",    description: "List custom fields.",                   inputSchema: { type: "object", properties: { account: { type: "string" } }, required: ["account"] } },
  { name: "page_create_custom_field",  description: "Create a custom field.",                inputSchema: { type: "object", properties: { account: { type: "string" }, name: { type: "string" }, type: { type: "string", enum: ["text","number","date","datetime","boolean"] }, description: { type: "string" } }, required: ["account", "name", "type"] } },
  { name: "page_get_flows",            description: "List all flows/automations.",           inputSchema: { type: "object", properties: { account: { type: "string" } }, required: ["account"] } },
  { name: "page_get_widgets",          description: "List widgets.",                         inputSchema: { type: "object", properties: { account: { type: "string" } }, required: ["account"] } },
  { name: "page_get_growth_tools",     description: "List growth tools.",                    inputSchema: { type: "object", properties: { account: { type: "string" } }, required: ["account"] } },
  { name: "page_get_otn_topics",       description: "List OTN topics.",                      inputSchema: { type: "object", properties: { account: { type: "string" } }, required: ["account"] } },
  { name: "page_get_bot_fields",       description: "List bot fields.",                      inputSchema: { type: "object", properties: { account: { type: "string" } }, required: ["account"] } },
  { name: "page_create_bot_field",     description: "Create a bot field.",                   inputSchema: { type: "object", properties: { account: { type: "string" }, name: { type: "string" }, type: { type: "string", enum: ["text","number","date","datetime","boolean"] }, description: { type: "string" } }, required: ["account", "name", "type"] } },
  { name: "page_set_bot_field",        description: "Set bot field value by ID.",            inputSchema: { type: "object", properties: { account: { type: "string" }, field_id: { type: "integer" }, field_value: { type: "string" } }, required: ["account", "field_id", "field_value"] } },
  { name: "page_set_bot_field_by_name",description: "Set bot field value by name.",          inputSchema: { type: "object", properties: { account: { type: "string" }, field_name: { type: "string" }, field_value: { type: "string" } }, required: ["account", "field_name", "field_value"] } },

  // Subscriber
  { name: "subscriber_get_info",                 description: "Get full subscriber info.",           inputSchema: { type: "object", properties: { account: { type: "string" }, subscriber_id: { type: "integer" } }, required: ["account", "subscriber_id"] } },
  { name: "subscriber_find_by_name",             description: "Search subscribers by name.",         inputSchema: { type: "object", properties: { account: { type: "string" }, name: { type: "string" } }, required: ["account", "name"] } },
  { name: "subscriber_find_by_custom_field",     description: "Search by custom field value.",       inputSchema: { type: "object", properties: { account: { type: "string" }, field_id: { type: "integer" }, field_value: { type: "string" } }, required: ["account", "field_id", "field_value"] } },
  { name: "subscriber_find_by_system_field",     description: "Search by email/phone.",              inputSchema: { type: "object", properties: { account: { type: "string" }, field_name: { type: "string" }, field_value: { type: "string" } }, required: ["account", "field_name", "field_value"] } },
  { name: "subscriber_create",                   description: "Create a new subscriber.",            inputSchema: { type: "object", properties: { account: { type: "string" }, first_name: { type: "string" }, last_name: { type: "string" }, phone: { type: "string" }, email: { type: "string" }, gender: { type: "string", enum: ["male","female"] }, has_opt_in_sms: { type: "boolean" }, has_opt_in_email: { type: "boolean" } }, required: ["account"] } },
  { name: "subscriber_update",                   description: "Update subscriber data.",             inputSchema: { type: "object", properties: { account: { type: "string" }, subscriber_id: { type: "integer" }, first_name: { type: "string" }, last_name: { type: "string" }, phone: { type: "string" }, email: { type: "string" }, has_opt_in_sms: { type: "boolean" }, has_opt_in_email: { type: "boolean" } }, required: ["account", "subscriber_id"] } },
  { name: "subscriber_add_tag",                  description: "Add tag by ID.",                      inputSchema: { type: "object", properties: { account: { type: "string" }, subscriber_id: { type: "integer" }, tag_id: { type: "integer" } }, required: ["account", "subscriber_id", "tag_id"] } },
  { name: "subscriber_add_tag_by_name",          description: "Add tag by name.",                    inputSchema: { type: "object", properties: { account: { type: "string" }, subscriber_id: { type: "integer" }, tag_name: { type: "string" } }, required: ["account", "subscriber_id", "tag_name"] } },
  { name: "subscriber_remove_tag",               description: "Remove tag by ID.",                   inputSchema: { type: "object", properties: { account: { type: "string" }, subscriber_id: { type: "integer" }, tag_id: { type: "integer" } }, required: ["account", "subscriber_id", "tag_id"] } },
  { name: "subscriber_remove_tag_by_name",       description: "Remove tag by name.",                 inputSchema: { type: "object", properties: { account: { type: "string" }, subscriber_id: { type: "integer" }, tag_name: { type: "string" } }, required: ["account", "subscriber_id", "tag_name"] } },
  { name: "subscriber_set_custom_field",         description: "Set custom field by ID.",             inputSchema: { type: "object", properties: { account: { type: "string" }, subscriber_id: { type: "integer" }, field_id: { type: "integer" }, field_value: { type: "string" } }, required: ["account", "subscriber_id", "field_id", "field_value"] } },
  { name: "subscriber_set_custom_field_by_name", description: "Set custom field by name.",           inputSchema: { type: "object", properties: { account: { type: "string" }, subscriber_id: { type: "integer" }, field_name: { type: "string" }, field_value: { type: "string" } }, required: ["account", "subscriber_id", "field_name", "field_value"] } },
  { name: "subscriber_set_custom_fields",        description: "Set multiple custom fields at once.", inputSchema: { type: "object", properties: { account: { type: "string" }, subscriber_id: { type: "integer" }, fields: { type: "array", items: { type: "object", properties: { field_id: { type: "integer" }, field_value: { type: "string" } }, required: ["field_id", "field_value"] } } }, required: ["account", "subscriber_id", "fields"] } },

  // Sending
  { name: "send_flow",    description: "Trigger a flow to a subscriber.",                    inputSchema: { type: "object", properties: { account: { type: "string" }, subscriber_id: { type: "integer" }, flow_ns: { type: "string", description: "Flow namespace from page_get_flows" } }, required: ["account", "subscriber_id", "flow_ns"] } },
  { name: "send_content", description: "Send custom content to a subscriber via Messenger.", inputSchema: { type: "object", properties: { account: { type: "string" }, subscriber_id: { type: "integer" }, message_tag: { type: "string", enum: ["ACCOUNT_UPDATE","POST_PURCHASE_UPDATE","CONFIRMED_EVENT_UPDATE","NON_PROMOTIONAL_SUBSCRIPTION"] }, messages: { type: "array", items: { type: "object" } } }, required: ["account", "subscriber_id", "message_tag", "messages"] } },
];

// ── Server ────────────────────────────────────────────────────────────────────

const server = new Server({ name: "manychat-mcp", version: "1.0.0" }, { capabilities: { tools: {} } });

server.setRequestHandler(ListToolsRequestSchema, async () => ({ tools: TOOLS }));

server.setRequestHandler(CallToolRequestSchema, async (req) => {
  const { name, arguments: args } = req.params;
  const acc = args?.account ?? "default";

  switch (name) {
    case "list_accounts":                    return ok({ accounts: Object.keys(ACCOUNTS) });

    case "page_get_info":                    return ok(await mcGet(acc, "/fb/page/getInfo"));
    case "page_get_tags":                    return ok(await mcGet(acc, "/fb/page/getTags"));
    case "page_create_tag":                  return ok(await mcPost(acc, "/fb/page/createTag", { name: args.name }));
    case "page_remove_tag":                  return ok(await mcPost(acc, "/fb/page/removeTag", { tag_id: args.tag_id }));
    case "page_get_custom_fields":           return ok(await mcGet(acc, "/fb/page/getCustomFields"));
    case "page_create_custom_field":         return ok(await mcPost(acc, "/fb/page/createCustomField", { name: args.name, type: args.type, ...(args.description && { description: args.description }) }));
    case "page_get_flows":                   return ok(await mcGet(acc, "/fb/page/getFlows"));
    case "page_get_widgets":                 return ok(await mcGet(acc, "/fb/page/getWidgets"));
    case "page_get_growth_tools":            return ok(await mcGet(acc, "/fb/page/getGrowthTools"));
    case "page_get_otn_topics":              return ok(await mcGet(acc, "/fb/page/getOtnTopics"));
    case "page_get_bot_fields":              return ok(await mcGet(acc, "/fb/page/getBotFields"));
    case "page_create_bot_field":            return ok(await mcPost(acc, "/fb/page/createBotField", { name: args.name, type: args.type, ...(args.description && { description: args.description }) }));
    case "page_set_bot_field":               return ok(await mcPost(acc, "/fb/page/setBotField", { field_id: args.field_id, field_value: args.field_value }));
    case "page_set_bot_field_by_name":       return ok(await mcPost(acc, "/fb/page/setBotFieldByName", { field_name: args.field_name, field_value: args.field_value }));

    case "subscriber_get_info":              return ok(await mcGet(acc, "/fb/subscriber/getInfo", { subscriber_id: args.subscriber_id }));
    case "subscriber_find_by_name":          return ok(await mcGet(acc, "/fb/subscriber/findByName", { name: args.name }));
    case "subscriber_find_by_custom_field":  return ok(await mcGet(acc, "/fb/subscriber/findByCustomField", { field_id: args.field_id, field_value: args.field_value }));
    case "subscriber_find_by_system_field":  return ok(await mcGet(acc, "/fb/subscriber/findBySystemField", { field_name: args.field_name, field_value: args.field_value }));
    case "subscriber_create":                return ok(await mcPost(acc, "/fb/subscriber/createSubscriber", Object.fromEntries(Object.entries(args).filter(([k]) => k !== "account"))));
    case "subscriber_update":                return ok(await mcPost(acc, "/fb/subscriber/updateSubscriber", Object.fromEntries(Object.entries(args).filter(([k]) => k !== "account"))));
    case "subscriber_add_tag":               return ok(await mcPost(acc, "/fb/subscriber/addTag", { subscriber_id: args.subscriber_id, tag_id: args.tag_id }));
    case "subscriber_add_tag_by_name":       return ok(await mcPost(acc, "/fb/subscriber/addTagByName", { subscriber_id: args.subscriber_id, tag_name: args.tag_name }));
    case "subscriber_remove_tag":            return ok(await mcPost(acc, "/fb/subscriber/removeTag", { subscriber_id: args.subscriber_id, tag_id: args.tag_id }));
    case "subscriber_remove_tag_by_name":    return ok(await mcPost(acc, "/fb/subscriber/removeTagByName", { subscriber_id: args.subscriber_id, tag_name: args.tag_name }));
    case "subscriber_set_custom_field":      return ok(await mcPost(acc, "/fb/subscriber/setCustomField", { subscriber_id: args.subscriber_id, field_id: args.field_id, field_value: args.field_value }));
    case "subscriber_set_custom_field_by_name": return ok(await mcPost(acc, "/fb/subscriber/setCustomFieldByName", { subscriber_id: args.subscriber_id, field_name: args.field_name, field_value: args.field_value }));
    case "subscriber_set_custom_fields":     return ok(await mcPost(acc, "/fb/subscriber/setCustomFields", { subscriber_id: args.subscriber_id, fields: args.fields }));

    case "send_flow":                        return ok(await mcPost(acc, "/fb/sending/sendFlow", { subscriber_id: args.subscriber_id, flow_ns: args.flow_ns }));
    case "send_content":                     return ok(await mcPost(acc, "/fb/sending/sendContent", { subscriber_id: args.subscriber_id, data: { version: "v2", content: { messages: args.messages, message_tag: args.message_tag } } }));

    default: return ok({ error: `Tool '${name}' not implemented.` });
  }
});

const transport = new StdioServerTransport();
await server.connect(transport);
