"""
Unit tests for the MCP authentication helper.
"""

import unittest
import base64
from src.mcp_auth import create_auth_headers


class TestMcpAuth(unittest.TestCase):

    def test_none_authentication(self):
        server = {
            'url': 'http://example.com',
            'authenticationMethod': 'None'
        }
        headers = create_auth_headers(server)
        self.assertNotIn('Authorization', headers)

    def test_basic_authentication(self):
        server = {
            'url': 'http://example.com',
            'authenticationMethod': 'Basic',
            'username': 'testuser',
            'password': 'testpass'
        }
        headers = create_auth_headers(server)

        self.assertIn('Authorization', headers)
        self.assertTrue(headers['Authorization'].startswith('Basic '))

        encoded = headers['Authorization'].replace('Basic ', '')
        decoded = base64.b64decode(encoded).decode('utf-8')
        self.assertEqual(decoded, 'testuser:testpass')

    def test_basic_authentication_missing_credentials(self):
        server = {
            'url': 'http://example.com',
            'authenticationMethod': 'Basic',
            'username': 'testuser'
            # password missing
        }
        with self.assertRaises(ValueError) as context:
            create_auth_headers(server)
        self.assertIn('username and password', str(context.exception))

    def test_bearer_authentication(self):
        server = {
            'url': 'http://example.com',
            'authenticationMethod': 'Bearer',
            'password': 'my-bearer-token'
        }
        headers = create_auth_headers(server)
        
        self.assertIn('Authorization', headers)        
        self.assertEqual(headers['Authorization'], 'Bearer my-bearer-token')

    def test_bearer_authentication_missing_token(self):
        server = {
            'url': 'http://example.com',
            'authenticationMethod': 'Bearer'
            # password/token missing
        }
        with self.assertRaises(ValueError) as context:
            create_auth_headers(server)
        self.assertIn('token', str(context.exception).lower())

    def test_pat_authentication(self):
        server = {
            'url': 'http://example.com',
            'authenticationMethod': 'PAT',
            'password': 'my-pat-token'
        }
        headers = create_auth_headers(server)
        
        self.assertIn('Authorization', headers)
        self.assertTrue(headers['Authorization'].startswith('Basic '))
        
        encoded = headers['Authorization'].replace('Basic ', '')
        decoded = base64.b64decode(encoded).decode('utf-8')
        self.assertEqual(decoded, ':my-pat-token')

    def test_custom_headers_preserved(self):
        server = {
            'url': 'http://example.com',
            'authenticationMethod': 'Bearer',
            'password': 'my-token',
            'headers': {
                'X-Custom-Header': 'custom-value',
                'X-Another-Header': 'another-value'
            }
        }
        headers = create_auth_headers(server)
        self.assertIn('Authorization', headers)
        self.assertEqual(headers['X-Custom-Header'], 'custom-value')
        self.assertEqual(headers['X-Another-Header'], 'another-value')


if __name__ == '__main__':
    unittest.main()
