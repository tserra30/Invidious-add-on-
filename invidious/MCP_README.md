# Home Assistant MCP Server

This MCP (Model Context Protocol) server provides programmatic access to Home Assistant's API using JSON-RPC 2.0 protocol.

## Overview

The MCP server runs alongside Invidious and provides a simple interface for AI assistants and other tools to interact with your Home Assistant instance.

## Available Methods

### 1. get_states
Get all entity states from Home Assistant.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "get_states",
  "params": {}
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": [
    {
      "entity_id": "light.living_room",
      "state": "on",
      "attributes": {...}
    },
    ...
  ]
}
```

### 2. get_state
Get a specific entity's state.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "get_state",
  "params": {
    "entity_id": "light.living_room"
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "entity_id": "light.living_room",
    "state": "on",
    "attributes": {
      "brightness": 255,
      "color_mode": "brightness"
    }
  }
}
```

### 3. call_service
Call a Home Assistant service.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "call_service",
  "params": {
    "domain": "light",
    "service": "turn_on",
    "entity_id": "light.living_room",
    "data": {
      "brightness": 128
    }
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": [
    {
      "entity_id": "light.living_room",
      "state": "on"
    }
  ]
}
```

### 4. get_addon_info
Get information about this add-on.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "get_addon_info",
  "params": {}
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "result": {
    "name": "Invidious",
    "version": "1.5.8",
    "state": "started"
  }
}
```

## Health Check

GET request to `/health`:
```bash
curl http://localhost:8099/health
```

Response:
```json
{
  "status": "ok",
  "service": "ha_mcp_server"
}
```

## Server Information

GET request to `/`:
```bash
curl http://localhost:8099/
```

Response:
```json
{
  "name": "Home Assistant MCP Server",
  "version": "1.0.0",
  "protocol": "mcp",
  "capabilities": [
    "get_states",
    "get_state",
    "call_service",
    "get_addon_info"
  ]
}
```

## Configuration

The MCP server reads the following environment variables:
- `MCP_PORT`: Port to listen on (default: 8099)
- `MCP_HOST`: Host to bind to (default: 127.0.0.1)
- `SUPERVISOR_TOKEN`: Home Assistant Supervisor API token (automatically provided)

## Usage Examples

### Using curl

```bash
# Get all entity states
curl -X POST http://localhost:8099 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "get_states"
  }'

# Turn on a light
curl -X POST http://localhost:8099 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "call_service",
    "params": {
      "domain": "light",
      "service": "turn_on",
      "entity_id": "light.bedroom"
    }
  }'
```

### Using Python

```python
import requests
import json

MCP_URL = "http://localhost:8099"

def mcp_call(method, params=None):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params or {}
    }
    response = requests.post(MCP_URL, json=payload)
    return response.json()

# Get all states
states = mcp_call("get_states")
print(json.dumps(states, indent=2))

# Turn on a light
result = mcp_call("call_service", {
    "domain": "light",
    "service": "turn_on",
    "entity_id": "light.living_room",
    "data": {"brightness": 255}
})
print(json.dumps(result, indent=2))
```

## Security

- The MCP server uses the Home Assistant Supervisor API token for authentication
- All requests to Home Assistant are authenticated automatically
- The server should only be exposed on trusted networks
- By default, the MCP port is not exposed externally

## Error Handling

Error responses follow JSON-RPC 2.0 format:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32601,
    "message": "Unknown method: invalid_method"
  }
}
```

Common error codes:
- `-32700`: Parse error
- `-32600`: Invalid request
- `-32601`: Method not found
- `-32602`: Invalid params
- `-32603`: Internal error
