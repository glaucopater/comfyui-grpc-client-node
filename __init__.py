import os
import subprocess
import sys
import socket
import atexit
import datetime

_server_process = None

def stop_server():
    global _server_process
    if _server_process:
        _server_process.terminate()
        try:
            _server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            _server_process.kill()
        _server_process = None

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Use 127.0.0.1 instead of localhost for consistency
        return s.connect_ex(('127.0.0.1', port)) == 0

# Start the server on module load, unless running tests
def start_server():
    global _server_process
    server_dir = os.path.join(os.path.dirname(__file__), "server")
    venv_python = os.path.join(server_dir, ".venv", "Scripts", "python.exe") if sys.platform == "win32" else os.path.join(server_dir, ".venv", "bin", "python")
    
    if is_port_in_use(50051):
        return

    print("gRPC Echo Server: Starting in background on port 50051 (gRPC)...")
    try:
        # Check if venv exists
        if os.path.exists(venv_python):
            cmd = [venv_python, "echo_server.py", "--parent-pid", str(os.getpid())]
        else:
            # Fallback to uv
            cmd = ["uv", "run", "echo_server.py", "--parent-pid", str(os.getpid())]
        
        _server_process = subprocess.Popen(
            cmd,
            cwd=server_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )
        atexit.register(stop_server)
    except Exception as e:
        print(f"gRPC Echo Server: Failed to start server: {e}")

if "pytest" not in sys.modules and "PYTEST_CURRENT_TEST" not in os.environ:
    start_server()

# Read version from VERSION file
version_path = os.path.join(os.path.dirname(__file__), "VERSION")
version = "unknown"
if os.path.exists(version_path):
    with open(version_path, "r") as f:
        version = f.read().strip()

try:
    from .grpc_echo_node import GRPCEchoNode
except (ImportError, ValueError):
    # Fallback for when imported as a standalone module (e.g. during tests)
    from grpc_echo_node import GRPCEchoNode

NODE_CLASS_MAPPINGS = {
    "GRPCEchoNode": GRPCEchoNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GRPCEchoNode": f"gRPC Echo (v{version})",
}

WEB_DIRECTORY = "js"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
