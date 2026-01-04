import os
import sys
import pytest
from unittest.mock import MagicMock, patch
import grpc

# Add root directory to path to import generated files and the node
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "server"))

from grpc_echo_node import GRPCEchoNode
import echo_pb2

@pytest.fixture
def node():
    return GRPCEchoNode()

@patch("grpc.secure_channel")
@patch("pathlib.Path.exists")
@patch("builtins.open")
def test_node_call_success(mock_open, mock_path_exists, mock_secure_channel, node):
    # Mock certificate file
    mock_path_exists.return_value = True
    mock_open.return_value.__enter__.return_value.read.return_value = b"mock_cert"
    
    # Mock gRPC channel and stub
    mock_stub = MagicMock()
    mock_stub.EchoOnce.return_value = echo_pb2.EchoReply(
        message="Echoing: hello",
        received_at="2024-01-01T12:00:00"
    )
    
    # Setup the sequence of events
    # mock_secure_channel() -> context manager -> channel -> stub
    mock_channel = MagicMock()
    mock_secure_channel.return_value.__enter__.return_value = mock_channel
    
    with patch("echo_pb2_grpc.EchoStub", return_value=mock_stub):
        result = node.call(host="localhost:50051", message="hello", cert_path="cert.pem")
    
    assert result == ("Echoing: hello", "2024-01-01T12:00:00")
    mock_stub.EchoOnce.assert_called_once()

def test_node_call_missing_cert(node):
    with patch("pathlib.Path.exists", return_value=False):
        result = node.call(host="localhost:50051", message="hello", cert_path="nonexistent.pem")
    
    assert "Error: Certificate file not found" in result[0]

@patch("grpc.secure_channel")
@patch("pathlib.Path.exists")
@patch("builtins.open")
def test_node_call_grpc_error(mock_open, mock_path_exists, mock_secure_channel, node):
    mock_path_exists.return_value = True
    mock_open.return_value.__enter__.return_value.read.return_value = b"mock_cert"
    
    mock_channel = MagicMock()
    mock_secure_channel.return_value.__enter__.return_value = mock_channel
    
    mock_stub = MagicMock()
    mock_stub.EchoOnce.side_effect = grpc.RpcError("Connection failed")
    # gRPC errors usually have a details() method
    mock_stub.EchoOnce.side_effect.details = lambda: "Connection failed"
    
    with patch("echo_pb2_grpc.EchoStub", return_value=mock_stub):
        result = node.call(host="localhost:50051", message="hello", cert_path="cert.pem")
    
    assert "gRPC Error: Connection failed" in result[0]
