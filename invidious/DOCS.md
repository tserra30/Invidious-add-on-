# Home Assistant Add-on: Invidious

## How to use

This add-on provides Invidious, a privacy-friendly alternative YouTube frontend, along with an optional MCP (Model Context Protocol) server for AI assistant integration.

When started, it will:
- Initialize a PostgreSQL database for Invidious (stored in `/data/postgresql`)
- Generate a secure HMAC key for the instance
- Start the Invidious web interface on port 3000
- Optionally start an MCP server on port 3001 (if enabled)

Access the Invidious web interface through Home Assistant's Ingress panel or directly at:
`http://[your-home-assistant-ip]:3000`

## Configuration

### Basic Configuration

This add-on works out of the box with no configuration required for basic Invidious functionality.

### MCP Server Configuration

The add-on includes an optional MCP (Model Context Protocol) server that allows AI assistants to interact with your Home Assistant instance.

**Configuration Options:**

- `mcp_enabled` (boolean, default: `false`): Enable or disable the MCP server
- `mcp_port` (port, default: `3001`): Port for the MCP server to listen on

**Example Configuration:**

```yaml
mcp_enabled: true
mcp_port: 3001
```

### What is MCP?

MCP (Model Context Protocol) is a standardized protocol that allows AI assistants like Claude, ChatGPT, and others to interact with external services. When enabled, this add-on provides an MCP server that exposes your Home Assistant instance's API, allowing AI assistants to:

- Get the state of entities (lights, switches, sensors, etc.)
- Call Home Assistant services (turn lights on/off, adjust thermostats, etc.)
- Retrieve configuration and available services
- Access entity state history

### Using the MCP Server

Once enabled, the MCP server will be accessible at:
`http://[your-home-assistant-ip]:3001`

The server automatically uses the Home Assistant Supervisor API token for authentication, so no additional configuration is needed for security.

**Supported MCP Tools:**

- `get_states`: Get current state of entities
- `call_service`: Execute Home Assistant services
- `get_services`: List available services
- `get_config`: Retrieve Home Assistant configuration
- `get_history`: Get historical state data for entities

## Data Persistence

The following data is persisted in the `/data` directory:
- PostgreSQL database files
- HMAC key for the instance

This ensures your Invidious instance maintains its state across restarts.

## Security

The MCP server uses the Home Assistant Supervisor API with built-in authentication. It only has access to your Home Assistant instance and runs within the isolated add-on container.
