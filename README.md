# ComfyUI gRPC Client Node (v0.1.6)
![Python Tests](https://github.com/glaucopater/comfyui-grpc-client-node/actions/workflows/test.yml/badge.svg?branch=main)

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
- Accepts a message via `EchoOnce` RPC call.
- Returns the message.

**Dependencies:** (managed via `pyproject.toml`)
- grpcio >= 1.76.0
- grpcio-tools == 1.62.0
- protobuf >= 4.25.3, < 5

### 2. **ComfyUI Client Node** (root directory)

A set of custom nodes for ComfyUI that connect securely to the gRPC echo server.
- **gRPC Echo**: Sends a message and receives an echo.

## Architecture & Startup

The gRPC server and ComfyUI client are integrated to start automatically.

```text
  ComfyUI Startup
        │
        ▼
  Load Custom Node: comfyui-grpc-client-node
        │
        ├──────────────────────────┐
        ▼                          ▼
  __init__.py execution     Node Discovery
        │                          │
        ▼                          │
  Check Port 50051                 │
        │                          │
  ┌─────┴─────┐                    │
  ▼           ▼                    ▼
[In Use]   [Available]       GRPCEchoNode Registered
  │           │                    │
  ▼           ▼                    │
[Skip]   [Spawn Background]        │
              │                    │
              ▼                    │
        uv run echo_server.py      │
              │                    │
              ▼                    ▼
       gRPC Server Running <───> ComfyUI Workflow
```

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

3.  **Install/Sync Dependencies:**
    ```bash
    cd comfyui-grpc-client-node/server
    uv sync
    ```


### Running the Server

```bash
cd /path/to/ComfyUI/custom_nodes/comfyui-grpc-client-node/server
uv run echo_server.py
```

The server will start listening securely on `0.0.0.0:50051`.

### Using the Nodes in ComfyUI

1. Start the echo server (see above).
2. Start ComfyUI.
3. Add the desired node from the "network/grpc" category.

#### gRPC Echo Node
- **host**: Server address (default: `localhost:50051`).
- **message**: Message to send to the server.
- **cert_path**: Absolute path to the `certificate.pem` file.

5. Execute the workflow to receive the response.

### gRPC Reflection

The server now supports gRPC reflection. You can use tools like `grpcurl` or Bruno to discover services automatically without manually providing the `.proto` file:

```bash
grpcurl -insecure localhost:50051 list
```

## API Definition

The service is defined in `server/echo.proto`:

```protobuf
service Echo {
  rpc EchoOnce (EchoRequest) returns (EchoReply) {}
}

message EchoRequest {
  string message = 1;
}

message EchoReply {
  string message = 1;
  string received_at = 2;
}
```

## Development

### Regenerating Protocol Buffer Files

If you modify `echo.proto`, regenerate the Python files from within the `server` directory:

```bash
cd server
uv run python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. echo.proto
```

## Testing

To run the unit tests:

1. Ensure dependencies are installed:
   ```bash
   cd server
   uv sync
   cd ..
   ```
2. Run the tests from the root directory:
   ```bash
   uv run --project server python -m pytest tests
   ```

## Building

To create a clean deployment package for ComfyUI:

1. Ensure you are in the project root.
2. Run the build script:
   ```bash
   python build.py
   ```
3. The build will be created in `build/vX.X.X/comfyui-grpc-client-node`.

## License
See [LICENSE](LICENSE) for details.