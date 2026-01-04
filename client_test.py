import time
import grpc
import echo_pb2
import echo_pb2_grpc

CERT_PATH = 'server/certs/certificate.pem'
HOST = 'localhost:50051'

with open(CERT_PATH, 'rb') as f:
    creds = grpc.ssl_channel_credentials(root_certificates=f.read())

print('Creating secure channel to', HOST)
try:
    with grpc.secure_channel(HOST, creds) as channel:
        stub = echo_pb2_grpc.EchoStub(channel)
        resp = stub.EchoOnce(echo_pb2.EchoRequest(text='test'))
        print('Response:', resp.text)
except Exception as e:
    print('Client exception:', e)
