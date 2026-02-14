import sys
import subprocess

from boundless_aiogram.core import print_error, print_info, Colors, print_colored
from boundless_aiogram.core.config import load_config
from boundless_aiogram.core.shell import find_project_root


def cmd_run():
    project_root = find_project_root()
    if not project_root:
        print_error("Not inside a Boundless project (no main.py or .boundless found)")
        sys.exit(1)

    config = load_config(project_root)
    mode = config.get("server_mode", "polling") if config else "polling"

    if mode == "webhook":
        print_info("Starting bot in webhook mode (uvicorn)...")
        print_colored(f"  Mode: {Colors.GREEN}Webhook (FastAPI){Colors.ENDC}", Colors.DIM)
        subprocess.run(
            [sys.executable, "-m", "uvicorn", "webhook.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
            cwd=project_root,
        )
    elif mode == "both":
        env_mode = "--webhook" if "--webhook" in sys.argv else ""
        if "--webhook" in sys.argv:
            print_info("Starting bot in webhook mode (uvicorn)...")
            subprocess.run(
                [sys.executable, "-m", "uvicorn", "webhook.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
                cwd=project_root,
            )
        else:
            print_info("Starting bot in polling mode...")
            print_colored(f"  Tip: use {Colors.CYAN}boundless run --webhook{Colors.ENDC} for webhook mode", Colors.DIM)
            subprocess.run([sys.executable, "main.py"], cwd=project_root)
    else:
        print_info("Starting bot in polling mode...")
        subprocess.run([sys.executable, "main.py"], cwd=project_root)