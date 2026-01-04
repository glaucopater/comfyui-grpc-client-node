import os
import subprocess
import sys
import socket

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def start_server():
    server_dir = os.path.join(os.path.dirname(__file__), "server")
    server_script = os.path.join(server_dir, "echo_server.py")
    
    if is_port_in_use(50051):
        print("gRPC Echo Server: Port 50051 (gRPC) already in use, assuming server is already running.")
        return

    print("gRPC Echo Server: Starting in background on port 50051 (gRPC)...")
    # Use uv run to start the server
    try:
        # Start in background without blocking ComfyUI
        subprocess.Popen(
            ["uv", "run", "echo_server.py"],
            cwd=server_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )
    except Exception as e:
        print(f"gRPC Echo Server: Failed to start server: {e}")

# Start the server on module load
start_server()

# Read version from VERSION file
version_path = os.path.join(os.path.dirname(__file__), "VERSION")
version = "unknown"
if os.path.exists(version_path):
    with open(version_path, "r") as f:
        version = f.read().strip()

from grpc_echo_node import GRPCEchoNode

NODE_CLASS_MAPPINGS = {
    "GRPCEchoNode": GRPCEchoNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GRPCEchoNode": f"gRPC Echo (v{version})",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
