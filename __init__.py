from .grpc_echo_node import GRPCEchoNode

NODE_CLASS_MAPPINGS = {
    "GRPCEchoNode": GRPCEchoNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GRPCEchoNode": "gRPC Echo",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
