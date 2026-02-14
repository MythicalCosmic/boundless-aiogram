import subprocess
from typing import List, Optional

from boundless_aiogram.core import Colors, print_colored


def run_command(command: List[str], cwd: Optional[str] = None) -> bool:
    try:
        subprocess.run(command, check=True, cwd=cwd, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        if e.stderr:
            print_colored(f"\n    {e.stderr.strip()}", Colors.RED + Colors.DIM)
        return False


def pip_freeze(cwd: str) -> str:
    import sys
    result = subprocess.run(
        [sys.executable, "-m", "pip", "freeze"],
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    return result.stdout