# ComfyUI gRPC Client Node

A gRPC-based integration for ComfyUI that enables secure communication with a simple echo service. This project is a ComfyUI custom node that includes a gRPC server.

## Project Structure

```
comfyui-grpc-client-node/
├── __init__.py               # ComfyUI custom node entry point
├── grpc_echo_node.py         # GRPCEchoNode implementation
├── server/                    # gRPC server and related files
│   ├── certs/                # SSL/TLS certificates
│   │   ├── certificate.pem
│   │   └── private.key
│   ├── echo.proto            # Protocol Buffer definition
│   ├── echo_pb2.py           # Generated protobuf code
│   ├── echo_pb2_grpc.py      # Generated gRPC code
│   ├── echo_server.py        # Echo service server
│   ├── pyproject.toml        # Python project configuration
│   └── src/
└── LICENSE                    # MIT License
```

## Overview

This project consists of two main components:

### 1. **Echo gRPC Server** (inside `server/`)

A simple gRPC server that implements an echo service. It:
- Listens on `0.0.0.0:50051` using a secure SSL/TLS channel.
- Accepts text messages via `EchoOnce` RPC call.
- Accepts a JSON string via `PrettifyJson` RPC call and returns it in a prettified format.
- Returns the text prefixed with "Echo: ".

**Dependencies:**
- grpcio >= 1.76.0
- grpcio-tools == 1.62.0
- protobuf >= 4.25.3, < 5

### 2. **ComfyUI Client Node** (root directory)

A set of custom nodes for ComfyUI that connect securely to the gRPC echo server.
- **gRPC Echo**: Sends a simple text message and receives an echo.
- **gRPC Prettify JSON**: Sends a JSON string and receives a formatted version.

## Getting Started

### Prerequisites

- Python >= 3.12
- OpenSSL (for generating certificates)
- A running ComfyUI instance

### Installation

1.  **Clone the repository** into your ComfyUI `custom_nodes` directory:
    ```bash
    cd /path/to/ComfyUI/custom_nodes
    git clone https://github.com/glaucopater/comfyui-grpc-client-node.git
    ```

2.  **Generate SSL Certificates:**
    ```bash
    cd comfyui-grpc-client-node/server
    openssl req -x509 -newkey rsa:4096 -keyout certs/private.key -out certs/certificate.pem -sha256 -days 365 -nodes -subj "/CN=localhost"
    ```

3.  **Install Server Dependencies:**
    ```bash
    cd ../.. # Back to the custom_nodes directory
    cd comfyui-grpc-client-node
    pip install -r server/requirements.txt # Assuming you have a requirements.txt in the server folder
    ```
    *Note: If you don't have a `requirements.txt`, you can install the dependencies manually from the `server/pyproject.toml` file.*


### Running the Server

```bash
cd /path/to/ComfyUI/custom_nodes/comfyui-grpc-client-node/server
python echo_server.py
```

The server will start listening securely on `0.0.0.0:50051`.

### Using the Nodes in ComfyUI

1. Start the echo server (see above).
2. Start ComfyUI.
3. Add the desired node from the "network/grpc" category.

#### gRPC Echo Node
- **host**: Server address (default: `localhost:50051`).
- **text**: Message to send to the server.
- **cert_path**: Absolute path to the `certificate.pem` file.

#### gRPC Prettify JSON Node
- **host**: Server address (default: `localhost:50051`).
- **json_text**: JSON string to be prettified.
- **cert_path**: Absolute path to the `certificate.pem` file.

5. Execute the workflow to receive the response.

## API Definition

The service is defined in `server/echo.proto`:

```protobuf
service Echo {
  rpc EchoOnce (EchoRequest) returns (EchoReply) {}
  rpc PrettifyJson (PrettifyJsonRequest) returns (PrettifyJsonResponse) {}
}

message EchoRequest {
  string text = 1;
}

message EchoReply {
  string text = 1;
}

message PrettifyJsonRequest {
  string json_text = 1;
}

message PrettifyJsonResponse {
  string prettified_json_text = 1;
}
```

## Development

### Regenerating Protocol Buffer Files

If you modify `echo.proto`, regenerate the Python files from within the `server` directory:

```bash
cd server
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. echo.proto
```

## License

MIT License © 2025 Glauco Pater

See [LICENSE](LICENSE) for details.