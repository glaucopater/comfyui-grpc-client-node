import os
import sys
import pytest
from unittest.mock import MagicMock
import grpc

# Add server directory to path to import generated files
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "server"))

import echo_pb2
from echo_server import EchoService

@pytest.fixture
def servicer():
    return EchoService()

@pytest.fixture
def mock_context():
    context = MagicMock(spec=grpc.ServicerContext)
    return context

def test_echo_once_success(servicer, mock_context):
    request = echo_pb2.EchoRequest(message="Hello test")
    response = servicer.EchoOnce(request, mock_context)
    
    assert response.message == "Hello test"
    assert response.received_at != ""
    mock_context.set_code.assert_not_called()

def test_echo_once_empty_message(servicer, mock_context):
    request = echo_pb2.EchoRequest(message="")
    response = servicer.EchoOnce(request, mock_context)
    
    # Validation should trigger
    mock_context.set_code.assert_called_once_with(grpc.StatusCode.INVALID_ARGUMENT)
    mock_context.set_details.assert_called_once()
    assert response.message == ""
