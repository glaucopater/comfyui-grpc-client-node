import json
from concurrent import futures
from pathlib import Path
import grpc
import echo_pb2
import echo_pb2_grpc


class EchoService(echo_pb2_grpc.EchoServicer):
    def EchoOnce(self, request, context):
        print(f"Server got: {request.text!r}")
        # Just echo back the text
        return echo_pb2.EchoReply(text=f"Echo: {request.text}")

    def PrettifyJson(self, request, context):
        print(f"Server received PrettifyJson request.")
        print(f"Raw json_text: {repr(request.json_text)}")

        if request.json_text == '[object Object]':
            print("Error: Received '[object Object]'. The input is not a valid JSON string.")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Received '[object Object]'. This usually means a JavaScript object was converted to a string incorrectly. Please ensure the input is a raw JSON string.")
            return echo_pb2.PrettifyJsonResponse()

        try:
            parsed_json = json.loads(request.json_text)
            prettified_json = json.dumps(parsed_json, indent=4)
            return echo_pb2.PrettifyJsonResponse(prettified_json_text=prettified_json)
        except json.JSONDecodeError as e:
            print(f"JSONDecodeError: {e}")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(f"Invalid JSON: {e}")
            return echo_pb2.PrettifyJsonResponse()


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    echo_pb2_grpc.add_EchoServicer_to_server(EchoService(), server)

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
