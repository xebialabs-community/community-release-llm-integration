import base64
from typing import Dict, Optional


def create_auth_headers(server: Dict) -> Dict[str, str]:
    """Create authentication headers from server config (mirrors HttpRequest.py logic)."""
    headers = {}
    
    if 'headers' in server and server['headers']:
        headers.update(server['headers'])
    
    auth_method = server.get('authenticationMethod')
    if auth_method:
        auth_method = str(auth_method)
    
    if not auth_method or auth_method == 'None':
        return headers
        
    elif auth_method == 'Basic':
        # Basic authentication: Base64(username:password)
        username = server.get('username')
        password = server.get('password')
        if not username or not password:
            raise ValueError("Basic authentication requires both username and password")
        
        credentials = f"{username}:{password}"
        encoded = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        headers['Authorization'] = f'Basic {encoded}'
        
    elif auth_method == 'Bearer':
        token = server.get('password')
        if not token:
            raise ValueError("Bearer authentication requires a token in the password field")
        
        headers['Authorization'] = f'Bearer {token}'
        
    elif auth_method == 'PAT':
        token = server.get('password')
        if not token:
            raise ValueError("PAT authentication requires a token in the password field")
        
        credentials = f":{token}"
        encoded = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        headers['Authorization'] = f'Basic {encoded}'

    return headers
