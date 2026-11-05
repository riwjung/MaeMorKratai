#!/usr/bin/env python3
"""Operator password setup. Values stay in Keychain and are never printed."""
import getpass
import json
import secrets
import subprocess
import sys
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import keyring

CONFIG = "maemorkratai-workshop-standalone"
PASSWORDS = "maemorkratai-workshop-passwords"


def request(path, method="GET", body=None, public=False):
    base = keyring.get_password(CONFIG, "NEXT_PUBLIC_SUPABASE_URL")
    key = keyring.get_password(
        CONFIG, "NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY" if public else "SUPABASE_SECRET_KEY"
    )
    if not base or not key:
        raise RuntimeError("ตั้งค่า scripts/credentials.py configure ก่อน")
    data = json.dumps(body).encode() if body is not None else None
    req = Request(base.rstrip("/") + path, data=data, method=method,
                  headers={"apikey": key, "Authorization": "Bearer " + key,
                           "Content-Type": "application/json"})
    try:
        with urlopen(req, timeout=30) as response:
            payload = response.read()
            return json.loads(payload) if payload else None
    except HTTPError as error:
        # Never print the request body, headers, token, password or raw response.
        raise RuntimeError(f"Supabase ตอบ HTTP {error.code}; ตรวจ key/สิทธิ์และลองใหม่") from None


def member(email):
    for page in range(1, 1001):
        result = request(f"/auth/v1/admin/users?page={page}&per_page=100")
        users = result.get("users", [])
        user = next((u for u in users if u.get("email", "").lower() == email), None)
        if user:
            rows = request(f"/rest/v1/workshop_members?select=active&user_id=eq.{user['id']}")
            if len(rows) != 1 or not rows[0]["active"]:
                raise RuntimeError("บัญชีนี้ยังไม่มีสิทธิ์ หรือถูกระงับแล้ว")
            return user
        if len(users) < 100:
            break
    raise RuntimeError("ยังไม่มีบัญชีนี้ ใช้ manage.mjs add-user ก่อน")


def provision(email, reset=False, password=None):
    """Only changes existing active members; a repeat keeps their saved password."""
    email = email.strip().lower()
    user = member(email)
    previous = keyring.get_password(PASSWORDS, email)
    if previous and not reset:
        session = request("/auth/v1/token?grant_type=password", "POST",
                          {"email": email, "password": previous}, public=True)
        if session.get("user", {}).get("id") != user["id"]:
            raise RuntimeError("ตรวจบัญชีไม่สำเร็จ")
        return "รหัสเดิมใน Keychain ใช้เข้าได้แล้ว"
    value = password or secrets.token_urlsafe(24)
    if len(value) < 12:
        raise RuntimeError("ใช้รหัสผ่านอย่างน้อย 12 ตัว")
    # Save before the network request so a lost response never loses the password.
    keyring.set_password(PASSWORDS, email, value)
    request(f"/auth/v1/admin/users/{user['id']}", "PUT",
            {"password": value, "email_confirm": True})
    session = request("/auth/v1/token?grant_type=password", "POST",
                      {"email": email, "password": value}, public=True)
    if session.get("user", {}).get("id") != user["id"]:
        raise RuntimeError("ตั้งค่าแล้วแต่ตรวจบัญชีไม่สำเร็จ รหัสยังอยู่ใน Keychain")
    return "ตั้งรหัสผ่านและตรวจการเข้าใช้แล้ว เก็บรหัสไว้ใน Keychain"


def main():
    if "macOS" not in type(keyring.get_keyring()).__module__:
        raise RuntimeError("ต้องใช้ macOS Keychain")
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode not in ("provision", "copy", "reset"):
        raise RuntimeError("ใช้: passwords.py provision | copy | reset")
    email = input("อีเมลที่ได้รับสิทธิ์: ").strip().lower()
    if mode == "copy":
        password = keyring.get_password(PASSWORDS, email)
        if not password:
            raise RuntimeError("ยังไม่มีรหัสผ่านของบัญชีนี้ใน Keychain")
        subprocess.run(["pbcopy"], input=password.encode(), check=True)
        print("คัดลอกรหัสผ่านแล้ว วางในช่องรหัสผ่านบนเว็บได้")
    elif mode == "reset":
        value = getpass.getpass("รหัสใหม่ (อย่างน้อย 12 ตัว; เว้นว่างเพื่อสุ่ม): ")
        if value and value != getpass.getpass("ยืนยันรหัสใหม่: "):
            raise RuntimeError("รหัสยืนยันไม่ตรง")
        print(provision(email, reset=True, password=value or None))
    else:
        print(provision(email))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(str(error) if isinstance(error, RuntimeError) else "ทำรายการไม่สำเร็จ กรุณาลองใหม่", file=sys.stderr)
        sys.exit(1)
