# MCP Server Catalog

Used by `core/mcp-integrations/SKILL.md` to enumerate available MCP servers, their
tools, resources, and connection details.

---

## What is an MCP Server

An MCP (Model Context Protocol) server exposes tools and resources that AI skills can
invoke using the standardized MCP protocol. Apotheon routes to MCP servers via the
Connector Hub using the `mcp` connector type.

---

## Registered MCP Servers

### Figma MCP Server

| Property | Value |
|---|---|
| Connector ID | `figma-mcp` |
| Transport | HTTP (Streamable) |
| Endpoint | `https://figma.com/api/mcp` (via claude.ai Figma integration) |
| Auth | OAuth2 (Figma account) |

**Available Tools:**
| Tool | Description |
|---|---|
| `get_design_context` | Retrieve design file with code, screenshot, and contextual hints |
| `get_screenshot` | Capture a Figma frame or component as an image |
| `get_metadata` | File metadata without full design context |
| `get_variable_defs` | Design tokens and variables |
| `get_libraries` | Available shared libraries and components |
| `generate_diagram` | Create a diagram in FigJam |

**Usage**: Load when a frontend engineering task requires design specs or token values.

---

### GitHub MCP Server

| Property | Value |
|---|---|
| Connector ID | `github-mcp` |
| Transport | Stdio or HTTP |
| Auth | GitHub Personal Access Token |

**Available Tools:**
| Tool | Description |
|---|---|
| `get_file_contents` | Read file contents from a repo |
| `list_commits` | List commits with filtering |
| `create_pull_request` | Open a PR with title, body, base, head |
| `create_issue` | Create a GitHub issue |
| `search_code` | Search across repositories |
| `get_pull_request` | Get PR details including diff |
| `list_workflow_runs` | List CI/CD workflow runs |

---

### Filesystem MCP Server

| Property | Value |
|---|---|
| Connector ID | `filesystem-mcp` |
| Transport | Stdio (local) |
| Auth | Path permissions |

**Available Tools:**
| Tool | Description |
|---|---|
| `read_file` | Read file at a local path |
| `write_file` | Write content to a local file |
| `list_directory` | List files and directories |
| `search_files` | Search for files by name pattern |
| `get_file_info` | File metadata (size, modified date) |

**Usage**: Primary file access mechanism for local-first workflows.

---

### Apotheon Internal MCP Server (planned)

| Property | Value |
|---|---|
| Connector ID | `apotheon-mcp` |
| Transport | HTTP (local) |
| Auth | Internal token |

**Planned Tools:**
| Tool | Description |
|---|---|
| `get_memory_packet` | Retrieve current workflow memory packet |
| `update_memory_packet` | Write updates to memory packet |
| `query_knowledge_graph` | GraphRAG query against organizational graph |
| `get_telemetry` | Retrieve recent telemetry events |
| `trigger_workflow` | Start a new SDLC or GTM workflow |

---

## MCP Tool Call Format

```json
{
  "method": "tools/call",
  "params": {
    "name": "[tool_name]",
    "arguments": {
      "[param]": "[value]"
    }
  }
}
```

Always call `tools/list` first in a new session to verify tool availability. Never
assume a tool exists without confirming via the catalog or a live `tools/list` response.

---

## Error Codes

| MCP Error Code | Meaning | Action |
|---|---|---|
| -32601 | Method not found | Check tool name; re-query tools/list |
| -32602 | Invalid params | Validate against tool schema before retry |
| -32603 | Internal server error | Retry with exponential backoff; escalate if persists |
| -32700 | Parse error | Fix malformed JSON payload |
| CONN-008 | Connector degraded | Wait for recovery; use REST fallback if available |