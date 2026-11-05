#!/usr/bin/env python3
"""Keep credentials in macOS Keychain; inject into a child process, never a file."""
import getpass
import os
import subprocess
import sys
from urllib.parse import urlparse

import keyring

SERVICE = "maemorkratai-workshop-standalone"
KEYS = ("NEXT_PUBLIC_SUPABASE_URL", "NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY", "SUPABASE_SECRET_KEY")


def main():
    command = sys.argv[1] if len(sys.argv) > 1 else "status"
    if "macOS" not in type(keyring.get_keyring()).__module__:
        raise SystemExit("ต้องใช้ macOS Keychain backend; ไม่ใช้ plaintext fallback")
    if command == "configure":
        for name in KEYS:
            value = getpass.getpass(f"{name} (เว้นว่างเพื่อใช้ค่าเดิม): ").strip()
            if not value:
                continue
            if name.endswith("_URL"):
                url = urlparse(value)
                if url.scheme != "https" or not url.hostname or url.username or url.query:
                    raise SystemExit("Supabase URL ต้องเป็น HTTPS URL ของโปรเจกต์")
                value = value.rstrip("/")
            keyring.set_password(SERVICE, name, value)
        print("บันทึกใน Keychain แล้ว ไม่มีการเขียน .env")
    elif command == "status":
        for name in KEYS:
            print(f"{name}: {'พร้อม' if keyring.get_password(SERVICE, name) else 'ยังไม่ได้ตั้งค่า'}")
    elif command == "run" and len(sys.argv) > 2:
        env = os.environ.copy()
        for name in KEYS:
            value = keyring.get_password(SERVICE, name)
            if not value:
                raise SystemExit(f"ยังไม่มี {name}; ใช้ configure ก่อน")
            env[name] = value
        result = subprocess.run(sys.argv[2:], env=env, check=False)
        raise SystemExit(result.returncode)
    else:
        raise SystemExit("ใช้: credentials.py configure | status | run <command> [args...]")


if __name__ == "__main__":
    main()
