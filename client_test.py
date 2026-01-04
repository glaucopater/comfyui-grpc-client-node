import sys
import grpc
from pathlib import Path

# Add the server directory to the path to import generated protobuf files
server_dir = Path(__file__).parent / "server"
sys.path.append(str(server_dir))

import echo_pb2
import echo_pb2_grpc

CERT_PATH = server_dir / 'certs' / 'certificate.pem'
HOST = 'localhost:50051'

with open(CERT_PATH, 'rb') as f:
    creds = grpc.ssl_channel_credentials(root_certificates=f.read())

print('Creating secure channel to', HOST)
try:
    with grpc.secure_channel(HOST, creds) as channel:
        stub = echo_pb2_grpc.EchoStub(channel)
        resp = stub.EchoOnce(echo_pb2.EchoRequest(message='test'))
        print(f'Response: {resp.message} (received at: {resp.received_at})')
except Exception as e:
    print('Client exception:', e)
