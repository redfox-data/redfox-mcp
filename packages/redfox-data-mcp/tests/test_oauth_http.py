import os
import unittest

from starlette.testclient import TestClient

os.environ.setdefault("REDFOX_MCP_AUTH_MODE", "oauth")
os.environ.setdefault("REDFOX_MCP_OAUTH_BASE_URL", "https://mcp.redfox.hk")


class OAuthRouteTests(unittest.TestCase):
    def test_discovery_and_api_key_still_reach_mcp(self):
        from redfox_data_mcp.oauth_http import build_app
        from redfox_data_mcp.server import mcp

        app = build_app(mcp)
        with TestClient(app) as client:
            metadata = client.get("/.well-known/oauth-authorization-server")
            self.assertEqual(metadata.status_code, 200, metadata.text)
            body = metadata.json()
            self.assertTrue(str(body["issuer"]).startswith("https://mcp.redfox.hk"))
            self.assertIn("/authorize", body["authorization_endpoint"])
            self.assertIn("/token", body["token_endpoint"])
            self.assertIn("/register", body["registration_endpoint"])
            protected = client.get("/.well-known/oauth-protected-resource/mcp")
            self.assertEqual(protected.status_code, 200, protected.text)
            self.assertIn("https://mcp.redfox.hk/mcp", protected.text)
            missing = client.post("/mcp", json={"jsonrpc": "2.0", "id": 1, "method": "initialize"})
            self.assertEqual(missing.status_code, 401)
            keyed = client.post(
                "/mcp",
                headers={
                    "REDFOX_API_KEY": "test-key",
                    "Accept": "application/json, text/event-stream",
                    "Content-Type": "application/json",
                },
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2025-03-26",
                        "capabilities": {},
                        "clientInfo": {"name": "t", "version": "0"},
                    },
                },
            )
            self.assertNotEqual(keyed.status_code, 401, keyed.text)


if __name__ == "__main__":
    unittest.main()
