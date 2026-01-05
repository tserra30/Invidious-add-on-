#!/usr/bin/env python3
"""
Example client for Home Assistant MCP Server
Demonstrates how to interact with the MCP server to control Home Assistant
"""

import json
import requests
from typing import Dict, Any, Optional

class HomeAssistantMCPClient:
    """Client for Home Assistant MCP Server"""
    
    def __init__(self, base_url: str = "http://localhost:8099"):
        """
        Initialize the MCP client
        
        Args:
            base_url: Base URL of the MCP server (default: http://localhost:8099)
        """
        self.base_url = base_url
        self.request_id = 0
    
    def _make_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a JSON-RPC request to the MCP server
        
        Args:
            method: The MCP method to call
            params: Optional parameters for the method
        
        Returns:
            The result from the MCP server
        """
        self.request_id += 1
        
        payload = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params or {}
        }
        
        response = requests.post(self.base_url, json=payload, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        
        if "error" in result:
            raise Exception(f"MCP Error: {result['error']['message']}")
        
        return result.get("result", {})
    
    def get_states(self) -> list:
        """Get all entity states from Home Assistant"""
        return self._make_request("get_states")
    
    def get_state(self, entity_id: str) -> Dict[str, Any]:
        """
        Get state of a specific entity
        
        Args:
            entity_id: The entity ID (e.g., 'light.living_room')
        """
        return self._make_request("get_state", {"entity_id": entity_id})
    
    def call_service(self, domain: str, service: str, entity_id: Optional[str] = None, 
                    data: Optional[Dict[str, Any]] = None) -> Any:
        """
        Call a Home Assistant service
        
        Args:
            domain: Service domain (e.g., 'light', 'switch')
            service: Service name (e.g., 'turn_on', 'turn_off')
            entity_id: Optional entity ID to target
            data: Optional service data
        """
        params = {
            "domain": domain,
            "service": service
        }
        if entity_id:
            params["entity_id"] = entity_id
        if data:
            params["data"] = data
        
        return self._make_request("call_service", params)
    
    def get_addon_info(self) -> Dict[str, Any]:
        """Get information about the Invidious addon"""
        return self._make_request("get_addon_info")
    
    def health_check(self) -> Dict[str, str]:
        """Check if the MCP server is healthy"""
        response = requests.get(f"{self.base_url}/health", timeout=5)
        response.raise_for_status()
        return response.json()
    
    def server_info(self) -> Dict[str, Any]:
        """Get MCP server information"""
        response = requests.get(self.base_url, timeout=5)
        response.raise_for_status()
        return response.json()


def example_usage():
    """Example usage of the MCP client"""
    
    # Initialize client
    # Change the URL to match your Home Assistant instance
    client = HomeAssistantMCPClient("http://homeassistant.local:8099")
    
    print("=" * 60)
    print("Home Assistant MCP Client Examples")
    print("=" * 60)
    
    # 1. Health check
    print("\n1. Health Check")
    print("-" * 40)
    try:
        health = client.health_check()
        print(f"Status: {health['status']}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 2. Server info
    print("\n2. Server Information")
    print("-" * 40)
    try:
        info = client.server_info()
        print(f"Name: {info['name']}")
        print(f"Version: {info['version']}")
        print(f"Capabilities: {', '.join(info['capabilities'])}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 3. Get all states
    print("\n3. Get All Entity States")
    print("-" * 40)
    try:
        states = client.get_states()
        print(f"Found {len(states)} entities")
        # Print first 3 entities as examples
        for state in states[:3]:
            entity_id = state.get('entity_id', 'unknown')
            state_value = state.get('state', 'unknown')
            print(f"  - {entity_id}: {state_value}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 4. Get specific entity state
    print("\n4. Get Specific Entity State")
    print("-" * 40)
    try:
        # Replace with an actual entity ID from your system
        entity_id = "light.living_room"
        state = client.get_state(entity_id)
        print(f"Entity: {state['entity_id']}")
        print(f"State: {state['state']}")
        print(f"Attributes: {json.dumps(state.get('attributes', {}), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 5. Turn on a light
    print("\n5. Call Service - Turn On Light")
    print("-" * 40)
    try:
        # Replace with an actual light entity ID from your system
        entity_id = "light.bedroom"
        result = client.call_service(
            domain="light",
            service="turn_on",
            entity_id=entity_id,
            data={"brightness": 128}
        )
        print(f"Result: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 6. Turn off a light
    print("\n6. Call Service - Turn Off Light")
    print("-" * 40)
    try:
        entity_id = "light.bedroom"
        result = client.call_service(
            domain="light",
            service="turn_off",
            entity_id=entity_id
        )
        print(f"Result: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 7. Get addon info
    print("\n7. Get Addon Information")
    print("-" * 40)
    try:
        addon_info = client.get_addon_info()
        print(f"Addon Info: {json.dumps(addon_info, indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    # Note: This will only work if the MCP server is running and accessible
    # Update the base URL to match your Home Assistant instance
    
    print("Home Assistant MCP Client")
    print("Make sure the Invidious add-on with MCP server is running!")
    print()
    
    try:
        example_usage()
    except requests.exceptions.ConnectionError:
        print("\n✗ Could not connect to MCP server")
        print("Please ensure:")
        print("  1. The Invidious add-on is running")
        print("  2. MCP is enabled in the add-on configuration")
        print("  3. The MCP server URL is correct")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
