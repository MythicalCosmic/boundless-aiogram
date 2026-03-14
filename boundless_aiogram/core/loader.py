from boundless_aiogram import Colors


class Loader:
    def __init__(self, message: str):
        self.message = message

    def __enter__(self):
        print(f"  {Colors.YELLOW}[*] {self.message}...{Colors.ENDC}", end="", flush=True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            print(f"\r  {Colors.GREEN}[+] {self.message} -- done{Colors.ENDC}")
        else:
            print(f"\r  {Colors.RED}[-] {self.message} -- failed{Colors.ENDC}")
        return False
