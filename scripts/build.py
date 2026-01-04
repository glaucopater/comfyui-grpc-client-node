import os
import shutil
import sys
import subprocess
from pathlib import Path

def build():
    # Setup paths relative to this script's location (scripts/build.py)
    root_dir = Path(__file__).parent.parent
    
    print("Step 1: Running tests...")
    try:
        subprocess.check_call([sys.executable, str(Path(__file__).parent / "test.py")])
    except subprocess.CalledProcessError:
        print("\nBuild aborted: Tests failed.")
        sys.exit(1)
        
    print("\nStep 2: Building package...")
    version_file = root_dir / "VERSION"
    
    if not version_file.exists():
        print(f"Error: VERSION file not found at {version_file}")
        sys.exit(1)
        
    with open(version_file, "r") as f:
        version = f.read().strip()
        
    build_root = root_dir / "build" / f"v{version}"
    dist_dir = build_root / "comfyui-grpc-client-node"
    
    print(f"Building version: {version}")
    
    # Create fresh build directory
    if build_root.exists():
        shutil.rmtree(build_root)
    dist_dir.mkdir(parents=True)
    
    # Files/directories to copy from root
    to_copy = [
        "__init__.py",
        "grpc_echo_node.py",
        "LICENSE",
        "README.md",
        "VERSION",
        "SUMMARY.md",
        "server",
        "js",
        "assets"
    ]
    
    # Patterns to exclude during directory copy
    exclude_patterns = shutil.ignore_patterns(
        "__pycache__", 
        "*.pyc", 
        ".venv", 
        "node_modules", 
        ".git",
        "build",
        ".pytest_cache"
    )
    
    for item in to_copy:
        src = root_dir / item
        dst = dist_dir / item
        
        if not src.exists():
            print(f"Warning: {item} not found, skipping.")
            continue
            
        if src.is_dir():
            print(f"Copying directory: {item}")
            shutil.copytree(src, dst, ignore=exclude_patterns)
        else:
            print(f"Copying file: {item}")
            shutil.copy2(src, dst)
            
    print(f"\nBuild completed successfully!")
    print(f"Location: {dist_dir}")

if __name__ == "__main__":
    build()
