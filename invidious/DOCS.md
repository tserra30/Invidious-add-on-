# Home Assistant Add-on: Invidious

## How to use

This add-on provides Invidious, a privacy-friendly alternative YouTube frontend, with integrated MCP (Model Context Protocol) server for Home Assistant API access.

When started, it will:
- Initialize a PostgreSQL database for Invidious (stored in `/data/postgresql`)
- Generate a secure HMAC key for the instance
- Start the Invidious web interface on port 3000
- Start the MCP server for Home Assistant integration (port 8099)

Access the Invidious web interface through Home Assistant's Ingress panel or directly at:
`http://[your-home-assistant-ip]:3000`

## MCP Server Integration

The add-on includes a Model Context Protocol (MCP) server that provides programmatic access to Home Assistant's API. This enables AI assistants and other tools to interact with your Home Assistant instance.

### MCP Server Features

The MCP server provides the following capabilities:
- **get_states**: Retrieve all entity states from Home Assistant
- **get_state**: Get a specific entity's state
- **call_service**: Call Home Assistant services
- **get_addon_info**: Get information about this add-on

### Using the MCP Server

The MCP server listens on port 8099 by default and uses JSON-RPC 2.0 protocol.

**Example Request - Get Entity State:**
```bash
curl -X POST http://[your-home-assistant-ip]:8099 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "get_state",
    "params": {"entity_id": "light.living_room"}
  }'
```

**Example Request - Call Service:**
```bash
curl -X POST http://[your-home-assistant-ip]:8099 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "call_service",
    "params": {
      "domain": "light",
      "service": "turn_on",
      "entity_id": "light.living_room",
      "data": {"brightness": 255}
    }
  }'
```

**Health Check:**
```bash
curl http://[your-home-assistant-ip]:8099/health
```

## Configuration

### Options

- **mcp_enabled** (bool, default: true): Enable or disable the MCP server
- **mcp_port** (port, default: 8099): Port for the MCP server to listen on

### Example Configuration

```yaml
mcp_enabled: true
mcp_port: 8099
```

To disable the MCP server:
```yaml
mcp_enabled: false
```

## Data Persistence

The following data is persisted in the `/data` directory:
- PostgreSQL database files
- HMAC key for the instance

This ensures your Invidious instance maintains its state across restarts.

## Security Notes

- The MCP server uses the Home Assistant Supervisor API token for authentication
- By default, the MCP port (8099) is not exposed externally unless you configure port forwarding
- The MCP server can only perform actions allowed by the Supervisor API
- It's recommended to keep the MCP server on the internal network only
