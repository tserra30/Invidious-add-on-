#!/usr/bin/env python3
"""
MCP Server for Home Assistant
Provides Model Context Protocol interface to Home Assistant API
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional

import aiohttp
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('mcp-ha-server')


class HomeAssistantMCPServer:
    """MCP Server that interfaces with Home Assistant"""
    
    def __init__(self, ha_url: str, ha_token: str):
        self.ha_url = ha_url.rstrip('/')
        self.ha_token = ha_token
        self.server = Server("home-assistant-mcp")
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Register handlers
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup MCP protocol handlers"""
        
        @self.server.list_tools()
        async def list_tools() -> List[types.Tool]:
            """List available Home Assistant tools"""
            return [
                types.Tool(
                    name="get_states",
                    description="Get the current state of all entities or a specific entity",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "entity_id": {
                                "type": "string",
                                "description": "Optional entity ID to get state for (e.g., 'light.living_room')"
                            }
                        }
                    }
                ),
                types.Tool(
                    name="call_service",
                    description="Call a Home Assistant service",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "domain": {
                                "type": "string",
                                "description": "Service domain (e.g., 'light', 'switch')"
                            },
                            "service": {
                                "type": "string",
                                "description": "Service name (e.g., 'turn_on', 'turn_off')"
                            },
                            "entity_id": {
                                "type": "string",
                                "description": "Optional entity ID to target"
                            },
                            "data": {
                                "type": "object",
                                "description": "Optional service data"
                            }
                        },
                        "required": ["domain", "service"]
                    }
                ),
                types.Tool(
                    name="get_services",
                    description="Get list of available services in Home Assistant",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                types.Tool(
                    name="get_config",
                    description="Get Home Assistant configuration",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                types.Tool(
                    name="get_history",
                    description="Get state history for entities",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "entity_id": {
                                "type": "string",
                                "description": "Entity ID to get history for"
                            },
                            "hours": {
                                "type": "number",
                                "description": "Number of hours of history to retrieve (default: 24)"
                            }
                        },
                        "required": ["entity_id"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
            """Handle tool calls"""
            try:
                if name == "get_states":
                    result = await self.get_states(arguments.get("entity_id"))
                elif name == "call_service":
                    result = await self.call_service(
                        arguments["domain"],
                        arguments["service"],
                        arguments.get("entity_id"),
                        arguments.get("data", {})
                    )
                elif name == "get_services":
                    result = await self.get_services()
                elif name == "get_config":
                    result = await self.get_config()
                elif name == "get_history":
                    result = await self.get_history(
                        arguments["entity_id"],
                        arguments.get("hours", 24)
                    )
                else:
                    result = {"error": f"Unknown tool: {name}"}
                
                return [types.TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            except Exception as e:
                logger.error(f"Error calling tool {name}: {e}", exc_info=True)
                return [types.TextContent(
                    type="text",
                    text=json.dumps({"error": str(e)}, indent=2)
                )]
    
    async def _api_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Any:
        """Make a request to Home Assistant API"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        headers = {
            "Authorization": f"Bearer {self.ha_token}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.ha_url}/api/{endpoint}"
        
        async with self.session.request(method, url, headers=headers, json=data) as response:
            response.raise_for_status()
            return await response.json()
    
    async def get_states(self, entity_id: Optional[str] = None) -> Dict[str, Any]:
        """Get entity states"""
        if entity_id:
            return await self._api_request("GET", f"states/{entity_id}")
        else:
            return await self._api_request("GET", "states")
    
    async def call_service(self, domain: str, service: str, entity_id: Optional[str] = None, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Call a Home Assistant service"""
        service_data = data or {}
        if entity_id:
            service_data["entity_id"] = entity_id
        
        return await self._api_request("POST", f"services/{domain}/{service}", service_data)
    
    async def get_services(self) -> Dict[str, Any]:
        """Get available services"""
        return await self._api_request("GET", "services")
    
    async def get_config(self) -> Dict[str, Any]:
        """Get Home Assistant config"""
        return await self._api_request("GET", "config")
    
    async def get_history(self, entity_id: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get entity history"""
        from datetime import datetime, timedelta
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        endpoint = f"history/period/{start_time.isoformat()}"
        params = f"?filter_entity_id={entity_id}"
        
        return await self._api_request("GET", f"{endpoint}{params}")
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()


async def main():
    """Main entry point for MCP server"""
    # Get configuration from environment
    ha_url = os.getenv("HA_URL", "http://supervisor/core")
    ha_token = os.getenv("SUPERVISOR_TOKEN", "")
    
    if not ha_token:
        logger.error("SUPERVISOR_TOKEN environment variable not set")
        sys.exit(1)
    
    logger.info(f"Starting MCP Server for Home Assistant at {ha_url}")
    
    # Create server instance
    mcp_server = HomeAssistantMCPServer(ha_url, ha_token)
    
    try:
        # Run the server
        async with stdio_server() as (read_stream, write_stream):
            await mcp_server.server.run(
                read_stream,
                write_stream,
                mcp_server.server.create_initialization_options()
            )
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        raise
    finally:
        await mcp_server.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
