import subprocess
import sys
from pathlib import Path

def run_tests():
    root_dir = Path(__file__).parent.parent
    
    print("Running unit tests using uv...")
    try:
        # Run pytest via uv
        subprocess.check_call([
            "uv", "run", "--project", "server", 
            "python", "-m", "pytest", str(root_dir / "tests")
        ], cwd=str(root_dir))
        print("\nAll tests passed!")
    except subprocess.CalledProcessError:
        print("\nSome tests failed.")
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
