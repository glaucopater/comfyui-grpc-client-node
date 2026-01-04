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



def serve():
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

    # Add secure port
    server.add_secure_port("[::]:50051", server_credentials)
    
    print("Echo gRPC server listening on 0.0.0.0:50051 (secure)")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
