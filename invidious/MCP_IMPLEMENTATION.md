# MCP Implementation Summary

## What Was Added

This implementation adds a complete Model Context Protocol (MCP) server to the Invidious Home Assistant add-on, enabling programmatic access to Home Assistant's API.

## Components

### 1. MCP Server (`ha_mcp_server.py`)
- **Location**: `/usr/local/bin/ha_mcp_server.py`
- **Language**: Python 3
- **Protocol**: JSON-RPC 2.0
- **Port**: 8099 (configurable)
- **Features**:
  - Get all entity states
  - Get specific entity state
  - Call Home Assistant services
  - Get add-on information
  - Health check endpoint
  - Server info endpoint

### 2. Service Integration
- **s6-overlay service**: Runs MCP server alongside Invidious
- **Configuration-aware**: Respects `mcp_enabled` setting
- **Automatic startup**: Starts with the add-on
- **Graceful shutdown**: Proper cleanup on service stop

### 3. Configuration
- **mcp_enabled** (bool, default: true): Enable/disable MCP server
- **mcp_port** (port, default: 8099): Port for MCP server

### 4. Documentation
- **DOCS.md**: User-facing documentation with examples
- **MCP_README.md**: Detailed API reference and usage guide
- **MCP_QUICK_REFERENCE.md**: Quick command reference
- **example_mcp_client.py**: Python client example

## How It Works

1. When the add-on starts, s6-overlay launches two services:
   - `invidious`: The main Invidious service (port 3000)
   - `mcp`: The MCP server (port 8099)

2. The MCP server connects to Home Assistant via the Supervisor API:
   - Uses `SUPERVISOR_TOKEN` environment variable (auto-provided)
   - Makes requests to `http://supervisor/core/api`
   - Proxies responses back as JSON-RPC

3. Clients can connect to the MCP server:
   - Send JSON-RPC 2.0 requests
   - Receive structured responses
   - Control Home Assistant entities and services

## API Methods

### get_states
```json
{"jsonrpc":"2.0","id":1,"method":"get_states","params":{}}
```
Returns all entity states from Home Assistant.

### get_state
```json
{"jsonrpc":"2.0","id":1,"method":"get_state","params":{"entity_id":"light.living_room"}}
```
Returns a specific entity's state.

### call_service
```json
{
  "jsonrpc":"2.0",
  "id":1,
  "method":"call_service",
  "params":{
    "domain":"light",
    "service":"turn_on",
    "entity_id":"light.bedroom",
    "data":{"brightness":255}
  }
}
```
Calls a Home Assistant service.

### get_addon_info
```json
{"jsonrpc":"2.0","id":1,"method":"get_addon_info","params":{}}
```
Returns information about the add-on.

## Security

- **Authentication**: Automatic via Supervisor API token
- **Network**: Default localhost only (127.0.0.1)
- **Port exposure**: Optional, disabled by default for external access
- **API access**: Limited to Supervisor API permissions

## Testing

All tests pass:
- ✓ Unit tests (JSON-RPC structure, parsing, validation)
- ✓ Integration tests (server start, health checks, endpoints)
- ✓ Configuration validation
- ✓ Python syntax validation
- ✓ Shell script syntax validation

## Version

- **Add-on version**: 1.5.8
- **MCP server version**: 1.0.0

## Files Changed/Added

### Modified:
- `invidious/config.yaml` - Added MCP configuration options
- `invidious/Dockerfile` - Added Python 3, made scripts executable
- `invidious/DOCS.md` - Added MCP documentation
- `invidious/CHANGELOG.md` - Added version 1.5.8 entry

### Added:
- `invidious/rootfs/usr/local/bin/ha_mcp_server.py` - MCP server
- `invidious/rootfs/etc/services.d/mcp/run` - MCP service startup
- `invidious/rootfs/etc/services.d/mcp/finish` - MCP service cleanup
- `invidious/MCP_README.md` - Detailed API documentation
- `invidious/MCP_QUICK_REFERENCE.md` - Quick reference guide
- `invidious/example_mcp_client.py` - Python client example
- `.gitignore` - Python cache exclusions

## Usage Example

```python
import requests

# Get all states
response = requests.post('http://localhost:8099', json={
    'jsonrpc': '2.0',
    'id': 1,
    'method': 'get_states'
})
states = response.json()['result']

# Turn on a light
requests.post('http://localhost:8099', json={
    'jsonrpc': '2.0',
    'id': 2,
    'method': 'call_service',
    'params': {
        'domain': 'light',
        'service': 'turn_on',
        'entity_id': 'light.bedroom'
    }
})
```

## Next Steps

To use the MCP server:

1. Install/update the Invidious add-on to version 1.5.8
2. The MCP server will start automatically (if enabled)
3. Access it at `http://[your-ha-ip]:8099`
4. Use the example client or create your own integration

For external access:
- Configure port forwarding in Home Assistant
- Expose port 8099
- Use appropriate network security
