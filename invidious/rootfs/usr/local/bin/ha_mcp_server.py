#!/usr/bin/env python3
"""
Home Assistant MCP Server
Provides Model Context Protocol interface for Home Assistant API
"""

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ha_mcp_server')

# Home Assistant Supervisor API configuration
SUPERVISOR_TOKEN = os.getenv('SUPERVISOR_TOKEN', '')
HA_API_BASE = 'http://supervisor/core/api'
ADDON_API_BASE = 'http://supervisor'


class HomeAssistantAPI:
    """Home Assistant API client"""
    
    def __init__(self, token):
        self.token = token
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
    
    def _make_request(self, url, method='GET', data=None):
        """Make HTTP request to Home Assistant API"""
        try:
            req = Request(url, headers=self.headers, method=method)
            if data:
                req.add_header('Content-Type', 'application/json')
                req.data = json.dumps(data).encode('utf-8')
            
            with urlopen(req, timeout=10) as response:
                return json.loads(response.read().decode('utf-8'))
        except HTTPError as e:
            logger.error(f"HTTP Error {e.code}: {e.reason}")
            return {'error': f'HTTP {e.code}: {e.reason}'}
        except URLError as e:
            logger.error(f"URL Error: {e.reason}")
            return {'error': str(e.reason)}
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            return {'error': str(e)}
    
    def get_states(self):
        """Get all entity states from Home Assistant"""
        url = f'{HA_API_BASE}/states'
        return self._make_request(url)
    
    def get_state(self, entity_id):
        """Get specific entity state"""
        url = f'{HA_API_BASE}/states/{entity_id}'
        return self._make_request(url)
    
    def call_service(self, domain, service, entity_id=None, data=None):
        """Call a Home Assistant service"""
        url = f'{HA_API_BASE}/services/{domain}/{service}'
        service_data = data or {}
        if entity_id:
            service_data['entity_id'] = entity_id
        return self._make_request(url, method='POST', data=service_data)
    
    def get_addon_info(self):
        """Get information about this addon"""
        url = f'{ADDON_API_BASE}/addons/self/info'
        return self._make_request(url)


class MCPRequestHandler(BaseHTTPRequestHandler):
    """MCP Protocol HTTP request handler"""
    
    def __init__(self, *args, ha_api=None, **kwargs):
        self.ha_api = ha_api
        super().__init__(*args, **kwargs)
    
    def do_POST(self):
        """Handle POST requests (MCP protocol)"""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        
        try:
            request = json.loads(body)
            response = self.handle_mcp_request(request)
            self.send_json_response(response)
        except json.JSONDecodeError:
            self.send_error_response(400, 'Invalid JSON')
        except Exception as e:
            logger.error(f"Error handling request: {str(e)}")
            self.send_error_response(500, str(e))
    
    def do_GET(self):
        """Handle GET requests (health check)"""
        if self.path == '/health':
            self.send_json_response({'status': 'ok', 'service': 'ha_mcp_server'})
        elif self.path == '/':
            self.send_json_response({
                'name': 'Home Assistant MCP Server',
                'version': '1.0.0',
                'protocol': 'mcp',
                'capabilities': [
                    'get_states',
                    'get_state',
                    'call_service',
                    'get_addon_info'
                ]
            })
        else:
            self.send_error_response(404, 'Not Found')
    
    def handle_mcp_request(self, request):
        """Handle MCP protocol request"""
        method = request.get('method')
        params = request.get('params', {})
        
        if method == 'get_states':
            return {
                'jsonrpc': '2.0',
                'id': request.get('id'),
                'result': self.ha_api.get_states()
            }
        
        elif method == 'get_state':
            entity_id = params.get('entity_id')
            if not entity_id:
                return self.error_response(request.get('id'), 'entity_id required')
            return {
                'jsonrpc': '2.0',
                'id': request.get('id'),
                'result': self.ha_api.get_state(entity_id)
            }
        
        elif method == 'call_service':
            domain = params.get('domain')
            service = params.get('service')
            if not domain or not service:
                return self.error_response(request.get('id'), 'domain and service required')
            
            result = self.ha_api.call_service(
                domain,
                service,
                params.get('entity_id'),
                params.get('data')
            )
            return {
                'jsonrpc': '2.0',
                'id': request.get('id'),
                'result': result
            }
        
        elif method == 'get_addon_info':
            return {
                'jsonrpc': '2.0',
                'id': request.get('id'),
                'result': self.ha_api.get_addon_info()
            }
        
        else:
            return self.error_response(request.get('id'), f'Unknown method: {method}')
    
    def error_response(self, request_id, message):
        """Create error response"""
        return {
            'jsonrpc': '2.0',
            'id': request_id,
            'error': {
                'code': -32601,
                'message': message
            }
        }
    
    def send_json_response(self, data, status=200):
        """Send JSON response"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def send_error_response(self, status, message):
        """Send error response"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        error_data = {'error': message, 'status': status}
        self.wfile.write(json.dumps(error_data).encode('utf-8'))
    
    def log_message(self, format, *args):
        """Override to use Python logging"""
        logger.info(format % args)


def create_handler(ha_api):
    """Create request handler with HA API instance"""
    def handler(*args, **kwargs):
        MCPRequestHandler(*args, ha_api=ha_api, **kwargs)
    return handler


def main():
    """Main server function"""
    # Check for supervisor token
    if not SUPERVISOR_TOKEN:
        logger.error("SUPERVISOR_TOKEN environment variable not set")
        logger.error("This server must run within a Home Assistant addon")
        sys.exit(1)
    
    # Initialize Home Assistant API client
    ha_api = HomeAssistantAPI(SUPERVISOR_TOKEN)
    
    # Server configuration
    port = int(os.getenv('MCP_PORT', '8099'))
    host = os.getenv('MCP_HOST', '127.0.0.1')
    
    # Create and start server
    handler = create_handler(ha_api)
    server = HTTPServer((host, port), handler)
    
    logger.info(f"Home Assistant MCP Server starting on {host}:{port}")
    logger.info("Available methods: get_states, get_state, call_service, get_addon_info")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
