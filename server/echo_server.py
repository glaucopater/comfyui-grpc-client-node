import argparse
import os
import time
import threading
import json
from datetime import datetime
from concurrent import futures
from pathlib import Path
import grpc
import echo_pb2
import echo_pb2_grpc
from grpc_reflection.v1alpha import reflection


class EchoService(echo_pb2_grpc.EchoServicer):
    def EchoOnce(self, request, context):
        print(f"Server got: {request.message!r}")
        if not request.message:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("The 'message' field is required and cannot be empty.")
            return echo_pb2.EchoReply()

        # Just echo back the message with timestamp
        return echo_pb2.EchoReply(
            message=request.message,
            received_at=datetime.now().isoformat()
        )



def monitor_parent(pid):
    """Monitor the parent process and exit if it's no longer running."""
    print(f"Server: Monitoring parent PID {pid}")
    
    if os.name == 'nt':
        # Windows-specific robust monitoring using ctypes
        import ctypes
        kernel32 = ctypes.windll.kernel32
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        STILL_ACTIVE = 259

        # Open process handle
        process_handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not process_handle:
            print("Server: Could not open parent process handle. Shutting down...")
            os._exit(0)

        try:
            while True:
                exit_code = ctypes.c_ulong()
                if not kernel32.GetExitCodeProcess(process_handle, ctypes.byref(exit_code)):
                    print("Server: Failed to get parent exit code. Shutting down...")
                    break
                
                if exit_code.value != STILL_ACTIVE:
                    print("Server: Parent process terminated. Shutting down...")
                    break
                time.sleep(2)
        finally:
            kernel32.CloseHandle(process_handle)
        os._exit(0)
    else:
        # Unix/Linux monitoring
        while True:
            try:
                os.kill(pid, 0)
            except OSError:
                print("Server: Parent process terminated. Shutting down...")
                os._exit(0)
            time.sleep(2)

def serve():
    parser = argparse.ArgumentParser()
    parser.add_argument("--parent-pid", type=int, help="PID of the parent process to monitor")
    args = parser.parse_args()

    if args.parent_pid:
        monitor_thread = threading.Thread(
            target=monitor_parent, 
            args=(args.parent_pid,), 
            daemon=True
        )
        monitor_thread.start()

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    echo_pb2_grpc.add_EchoServicer_to_server(EchoService(), server)

    # Enable reflection
    SERVICE_NAMES = (
        echo_pb2.DESCRIPTOR.services_by_name['Echo'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)

    # Read server credentials (paths resolved relative to this file)
    base_dir = Path(__file__).parent
    key_path = base_dir / "certs" / "private.key"
    cert_path = base_dir / "certs" / "certificate.pem"

    with open(key_path, "rb") as f:
        private_key = f.read()
    with open(cert_path, "rb") as f:
        certificate_chain = f.read()

    # Create server credentials
    server_credentials = grpc.ssl_server_credentials(
        ((private_key, certificate_chain),)
    )

    # Add secure port - use 0.0.0.0 for better IPv4 compatibility on Windows
    server.add_secure_port("0.0.0.0:50051", server_credentials)
    
    print("Echo gRPC server listening on 0.0.0.0:50051 (secure)")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
