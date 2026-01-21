#!/usr/bin/env python3
"""
Verify All Social Media Skills

Runs verification scripts for all social media posting skills.
"""

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

# Colors
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'

skills = [
    "posting-facebook",
    "posting-instagram",
    "posting-twitter"
]

def main():
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"  Verifying Social Media Skills")
    print(f"{'='*60}{Colors.END}\n")

    results = {}

    for skill in skills:
        verify_script = PROJECT_ROOT / ".claude" / "skills" / skill / "scripts" / "verify.py"

        if not verify_script.exists():
            print(f"{Colors.RED}[X]{Colors.END} {skill}: verify.py not found")
            results[skill] = False
            continue

        print(f"\nTesting {skill}...")
        try:
            result = subprocess.run(
                [sys.executable, str(verify_script)],
                capture_output=True,
                text=True,
                cwd=str(PROJECT_ROOT)
            )

            if result.returncode == 0:
                print(f"{Colors.GREEN}[OK]{Colors.END} {skill}: {result.stdout.strip()}")
                results[skill] = True
            else:
                print(f"{Colors.RED}[FAIL]{Colors.END} {skill}:")
                print(result.stdout)
                results[skill] = False

        except Exception as e:
            print(f"{Colors.RED}[ERROR]{Colors.END} {skill}: {str(e)}")
            results[skill] = False

    # Summary
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"  Summary")
    print(f"{'='*60}{Colors.END}\n")

    passed = sum(1 for r in results.values() if r)
    failed = sum(1 for r in results.values() if not r)

    for skill, result in results.items():
        status = f"{Colors.GREEN}PASS{Colors.END}" if result else f"{Colors.RED}FAIL{Colors.END}"
        print(f"{skill}: {status}")

    print(f"\n{Colors.BLUE}Total: {Colors.GREEN}{passed} passed{Colors.END}, "
          f"{Colors.RED}{failed} failed{Colors.END}\n")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
