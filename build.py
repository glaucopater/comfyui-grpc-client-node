import os
import shutil
import pathlib

def build():
    # 1. Get current version
    version_file = pathlib.Path("VERSION")
    if not version_file.exists():
        print("Error: VERSION file not found.")
        return
    
    version = version_file.read_text().strip()
    print(f"Building version: {version}")

    # 2. Define paths
    build_root = pathlib.Path("build")
    version_dir = build_root / f"v{version}"
    dist_dir = version_dir / "comfyui-grpc-client-node"

    # 3. Clean and recreate directory
    if version_dir.exists():
        print(f"Cleaning existing build directory: {version_dir}")
        shutil.rmtree(version_dir)
    
    dist_dir.mkdir(parents=True)

    # 4. Define files and directories to copy
    to_copy = [
        "__init__.py",
        "grpc_echo_node.py",
        "LICENSE",
        "README.md",
        "VERSION",
        "server"
    ]

    # Patterns to exclude during directory copy
    exclude_patterns = [
        ".venv",
        "__pycache__",
        "uv.lock",
        ".python-version",
        "error.log",
        "*.pyc",
        ".git"
    ]

    def ignore_func(directory, contents):
        ignored = []
        for item in contents:
            for pattern in exclude_patterns:
                if pathlib.Path(item).match(pattern):
                    ignored.append(item)
                    break
        return ignored

    # 5. Copy files
    for item_name in to_copy:
        src = pathlib.Path(item_name)
        if not src.exists():
            print(f"Warning: {item_name} not found, skipping.")
            continue
        
        dst = dist_dir / item_name
        if src.is_dir():
            print(f"Copying directory: {item_name}")
            shutil.copytree(src, dst, ignore=ignore_func)
        else:
            print(f"Copying file: {item_name}")
            shutil.copy2(src, dst)

    print(f"\nBuild completed successfully!")
    print(f"Location: {dist_dir.absolute()}")

if __name__ == "__main__":
    build()
