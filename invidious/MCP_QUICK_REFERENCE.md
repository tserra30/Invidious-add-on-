# MCP Server Quick Reference

## Connection

- **URL**: `http://[your-ha-ip]:8099`
- **Protocol**: JSON-RPC 2.0
- **Default Port**: 8099
- **Internal Only**: 127.0.0.1 (configurable)

## Health Endpoints

```bash
# Health check
curl http://localhost:8099/health

# Server info
curl http://localhost:8099/
```

## Methods

### 1. get_states
Get all Home Assistant entity states

```bash
curl -X POST http://localhost:8099 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"get_states","params":{}}'
```

### 2. get_state
Get a specific entity state

```bash
curl -X POST http://localhost:8099 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"get_state","params":{"entity_id":"light.living_room"}}'
```

### 3. call_service
Call a Home Assistant service

```bash
# Turn on a light
curl -X POST http://localhost:8099 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc":"2.0",
    "id":1,
    "method":"call_service",
    "params":{
      "domain":"light",
      "service":"turn_on",
      "entity_id":"light.bedroom",
      "data":{"brightness":255}
    }
  }'
```

### 4. get_addon_info
Get addon information

```bash
curl -X POST http://localhost:8099 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"get_addon_info","params":{}}'
```

## Configuration

Add-on options (via Home Assistant UI or config):

```yaml
mcp_enabled: true  # Enable/disable MCP server
mcp_port: 8099     # Port for MCP server
```

## Response Format

Success:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": { ... }
}
```

Error:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32601,
    "message": "Method not found"
  }
}
```

## Common Use Cases

**Turn on all lights:**
```bash
curl -X POST http://localhost:8099 -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"call_service","params":{"domain":"light","service":"turn_on"}}'
```

**Get sensor data:**
```bash
curl -X POST http://localhost:8099 -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"get_state","params":{"entity_id":"sensor.temperature"}}'
```

**Set thermostat:**
```bash
curl -X POST http://localhost:8099 -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"call_service","params":{"domain":"climate","service":"set_temperature","entity_id":"climate.living_room","data":{"temperature":22}}}'
```

## Python Client

See `example_mcp_client.py` for a complete Python client implementation.

## Security

- MCP server uses Supervisor API token (automatic)
- Default: localhost only (127.0.0.1)
- Configure port forwarding carefully
- Use on trusted networks only
