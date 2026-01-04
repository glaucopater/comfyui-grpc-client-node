import grpc
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock

# Add the server directory to the path to import generated protobuf files
server_dir = Path(__file__).parent / "server"
sys.path.append(str(server_dir))

import echo_pb2
import echo_pb2_grpc

# This import might fail if not running inside ComfyUI, so we'll mock it if needed elsewhere
try:
    from server import PromptServer
except ImportError:
    PromptServer = MagicMock() # For tests
from aiohttp import web

def run_grpc_test(host, cert_path):
    # Resolve certificate path: try given path, then path relative to this file
    cert_candidate = Path(cert_path)
    if not cert_candidate.exists():
        candidate = Path(__file__).parent / cert_path
        if candidate.exists():
            cert_candidate = candidate

    if not cert_candidate.exists():
        return {"success": False, "message": f"Certificate file not found at {cert_path}"}

    try:
        with open(cert_candidate, "rb") as f:
            server_certificate = f.read()

        credentials = grpc.ssl_channel_credentials(root_certificates=server_certificate)

        # Remove the (gRPC) suffix if present for the actual connection
        clean_host = host.split(" (")[0].strip()

        with grpc.secure_channel(clean_host, credentials) as channel:
            stub = echo_pb2_grpc.EchoStub(channel)
            # Use a tiny timeout for the test
            req = echo_pb2.EchoRequest(message="ping")
            resp = stub.EchoOnce(req, timeout=2) # 2 second timeout for test
        return {"success": True, "message": f"Connected! Server echoed: {resp.message}"}
    except grpc.RpcError as e:
        return {"success": False, "message": f"gRPC Error: {e.details()}"}
    except Exception as e:
        return {"success": False, "message": str(e)}

@PromptServer.instance.routes.post("/comfyui-grpc/test_connection")
async def test_connection_api(request):
    json_data = await request.json()
    host = json_data.get("host", "localhost:50051")
    cert_path = json_data.get("cert_path", "server/certs/certificate.pem")
    
    result = run_grpc_test(host, cert_path)
    return web.json_response(result)

class GRPCEchoNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "host": ("STRING", {"default": "localhost:50051 (gRPC)"}),
                "message": (
                    "STRING",
                    {
                        "default": "Hello from ComfyUI",
                        "multiline": True,
                    },
                ),
                "cert_path": ("STRING", {"default": "server/certs/certificate.pem"}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("message", "received_at")
    FUNCTION = "call"
    CATEGORY = "network/grpc"

    def call(self, host, message, cert_path):
        result = run_grpc_test(host, cert_path)
        if result["success"]:
            # Need to do a full call here because run_grpc_test just pings
            # (or we can modify run_grpc_test to take the message)
            # Let's just use the logic directly here for the real call to avoid confusion
            
            # Resolve cert path again (or pass it back from run_grpc_test)
            cert_candidate = Path(cert_path)
            if not cert_candidate.exists():
                cert_candidate = Path(__file__).parent / cert_path

            with open(cert_candidate, "rb") as f:
                server_certificate = f.read()
            credentials = grpc.ssl_channel_credentials(root_certificates=server_certificate)
            
            clean_host = host.split(" (")[0].strip()
            with grpc.secure_channel(clean_host, credentials) as channel:
                stub = echo_pb2_grpc.EchoStub(channel)
                req = echo_pb2.EchoRequest(message=message)
                resp = stub.EchoOnce(req)
            return (resp.message, resp.received_at)
        else:
            return (result["message"], "Error")



NODE_CLASS_MAPPINGS = {
    "GRPCEchoNode": GRPCEchoNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GRPCEchoNode": "gRPC Echo",
}
