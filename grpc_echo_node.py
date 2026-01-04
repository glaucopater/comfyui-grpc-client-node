import grpc
import os
import sys
from pathlib import Path

# Add the server directory to the path to import generated protobuf files
server_dir = Path(__file__).parent / "server"
sys.path.append(str(server_dir))

import echo_pb2
import echo_pb2_grpc

class GRPCEchoNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "host": ("STRING", {"default": "localhost:50051"}),
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
        # Resolve certificate path: try given path, then path relative to this file
        cert_candidate = Path(cert_path)
        if not cert_candidate.exists():
            candidate = Path(__file__).parent / cert_path
            if candidate.exists():
                cert_candidate = candidate

        if not cert_candidate.exists():
            return (f"Error: Certificate file not found at {cert_path}",)

        try:
            with open(cert_candidate, "rb") as f:
                server_certificate = f.read()

            credentials = grpc.ssl_channel_credentials(root_certificates=server_certificate)

            with grpc.secure_channel(host, credentials) as channel:
                stub = echo_pb2_grpc.EchoStub(channel)
                req = echo_pb2.EchoRequest(message=message)
                resp = stub.EchoOnce(req)
            return (resp.message, resp.received_at)
        except grpc.RpcError as e:
            return (f"gRPC Error: {e.details()}",)
        except Exception as e:
            return (f"An unexpected error occurred: {str(e)}",)



NODE_CLASS_MAPPINGS = {
    "GRPCEchoNode": GRPCEchoNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GRPCEchoNode": "gRPC Echo",
}
