import sys
import os
import subprocess
from pathlib import Path

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent

def main():
    print("🚀 Starting Digital FTE System (Unified Startup)...")
    
    service_manager_path = PROJECT_ROOT / "src" / "service_manager.py"
    
    if not service_manager_path.exists():
        print(f"❌ Error: Service Manager not found at {service_manager_path}")
        sys.exit(1)
        
    try:
        # Run service manager with --start-all
        subprocess.run(
            [sys.executable, str(service_manager_path), "--start-all"],
            cwd=str(PROJECT_ROOT),
            check=True
        )
    except KeyboardInterrupt:
        print("\n👋 System stopped.")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

