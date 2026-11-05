#!/usr/bin/env python3
"""Use Vercel from macOS Keychain without tokens in files or command arguments."""
import getpass
import json
import os
from pathlib import Path
import subprocess
import sys
from urllib.error import HTTPError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

import keyring

SERVICE = "maemorkratai-workshop-standalone"
CLI = ["npx", "--yes", "vercel@64.7.0"]


class VercelError(RuntimeError):
    def __init__(self, status, path, invalid_token=False):
        self.status = status
        if status == 404 and path == "/v2/user":
            message = (
                "Vercel ตอบ 404 ที่ /v2/user (ขั้นอ่านบัญชี ยังไม่ได้ deploy).\n"
                "ถ้าเลือก Scope เป็น Team/Project ให้ตรวจสิทธิ์อ่านข้อมูลบัญชี; "
                "CLI อาจต้องใช้ Full Account ของบัญชีส่วนตัวแบบอายุสั้น.\n"
                "ถ้าเป็น Full Account อยู่แล้ว อย่าเพิ่งสร้างซ้ำ แจ้ง HTTP 404 เพื่อวิเคราะห์ต่อ"
            )
        elif invalid_token or status == 401:
            message = "Vercel ไม่ยอมรับ token; ตรวจว่าคัดลอกค่าครบและ token ยังไม่หมดอายุหรือถูก revoke"
        elif status == 403:
            message = "Vercel ตอบ 403: token ไม่มีสิทธิ์ทำรายการนี้ใน scope ที่เลือก"
        else:
            message = f"Vercel ตอบ HTTP {status}; ยังทำรายการไม่สำเร็จ"
        super().__init__(message)


def api(token, path, method="GET", data=None):
    req = Request("https://api.vercel.com" + path, method=method,
                  data=json.dumps(data).encode() if data is not None else None,
                  headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"})
    try:
        with urlopen(req, timeout=30) as response:
            return json.load(response)
    except HTTPError as error:
        try:
            detail = json.loads(error.read()).get("error", {})
            invalid = detail.get("invalidToken") is True or detail.get("code") == "invalid_token"
        except (ValueError, AttributeError):
            invalid = False
        # Never echo a raw API body; it may contain request/credential details.
        raise VercelError(error.code, path, invalid) from None


def main():
    if "macOS" not in type(keyring.get_keyring()).__module__:
        raise RuntimeError("ต้องใช้ macOS Keychain")
    mode = sys.argv[1] if len(sys.argv) > 1 else "status"
    if mode == "configure":
        token = getpass.getpass("Vercel token จากบัญชีที่คุณควบคุมเอง: ").strip()
        if not token:
            raise RuntimeError("ยังไม่ได้กรอก token")
        profile = api(token, "/v2/user")["user"]
        keyring.set_password(SERVICE, "VERCEL_TOKEN", token)
        print("เก็บ token ใน Keychain แล้ว บัญชี:", profile.get("username", "ตรวจสำเร็จ"))
        return
    token = keyring.get_password(SERVICE, "VERCEL_TOKEN")
    if mode == "status":
        print("Vercel: " + ("มี token ใน Keychain" if token else "ยังไม่ได้เชื่อม"))
        return
    if not token:
        raise RuntimeError("ใช้ scripts/vercel.py configure ก่อน")
    if mode == "link" and len(sys.argv) == 3:
        # Only link the existing workshop. CLI `link --yes` also downloads an
        # OIDC token into .env.local; the REST lookup avoids that side effect.
        project = api(token, "/v9/projects/maemorkratai-workshop?" + urlencode({"slug": sys.argv[2]}))
        if project.get("name") != "maemorkratai-workshop" or not project.get("accountId"):
            raise RuntimeError("ตรวจชื่อและทีมของโปรเจกต์ห้องทดลองไม่สำเร็จ")
        path = Path(".vercel/project.json")
        if path.exists():
            linked = json.loads(path.read_text())
            if linked["projectId"] != project["id"] or linked["orgId"] != project["accountId"]:
                raise RuntimeError("โฟลเดอร์นี้ link กับโปรเจกต์อื่นอยู่ จึงไม่แก้ทับ")
        else:
            path.parent.mkdir(exist_ok=True)
            path.write_text(json.dumps({"projectId": project["id"], "orgId": project["accountId"],
                                        "projectName": project["name"]}, indent=2) + "\n")
        print("เชื่อม maemorkratai-workshop แล้ว ไม่มีการดาวน์โหลด token ลงไฟล์")
        return
    if mode == "run" and len(sys.argv) > 2:
        if sys.argv[2] in ("link", "login", "pull") or sys.argv[2:4] == ["env", "pull"]:
            raise RuntimeError("คำสั่งนี้อาจเขียน token/secret ลงไฟล์; ใช้ configure หรือ link <team-slug> ผ่านตัวช่วย")
        env = os.environ.copy()
        env["VERCEL_TOKEN"] = token
        env["VERCEL_TELEMETRY_DISABLED"] = "1"
        # This machine's shared npm cache contains files owned by root.
        # Use a project cache outside the source/vault without changing ownership.
        env["npm_config_cache"] = str(Path.home() / "AIVideoLocal/maemorkratai/.npm-cache-vercel")
        result = subprocess.run(CLI + sys.argv[2:], env=env, check=False)
        raise SystemExit(result.returncode)
    if mode == "env-production":
        link = json.loads(Path(".vercel/project.json").read_text())
        project_id, org_id = link["projectId"], link["orgId"]
        scope = {"teamId": org_id} if org_id.startswith("team_") else {}
        suffix = ("?" + urlencode(scope)) if scope else ""
        project = api(token, "/v9/projects/" + quote(project_id, safe="") + suffix)
        if project.get("name") != "maemorkratai-workshop":
            raise RuntimeError("โปรเจกต์ที่ link ไม่ใช่ maemorkratai-workshop; ยังไม่ได้แก้ environment")
        values = []
        for name in ("NEXT_PUBLIC_SUPABASE_URL", "NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY", "SUPABASE_SECRET_KEY"):
            value = keyring.get_password(SERVICE, name)
            if not value:
                raise RuntimeError(f"ยังไม่มี {name} ใน Keychain")
            values.append({"key": name, "value": value, "target": ["production"],
                           "type": "sensitive" if name == "SUPABASE_SECRET_KEY" else "encrypted"})
        query = urlencode({**scope, "upsert": "true"})
        result = api(token, "/v10/projects/" + quote(project_id, safe="") + "/env?" + query,
                     "POST", values)
        if result.get("failed"):
            raise RuntimeError("ตั้งค่าบางรายการไม่สำเร็จ ตรวจ Environment Variables บน Vercel")
        print("ตั้งค่าสาม environment variables สำหรับ production แล้ว โดยไม่เขียนค่าลงไฟล์")
        return
    raise RuntimeError("ใช้: vercel.py configure | status | link <team-slug> | run <CLI args> | env-production")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(str(error) if isinstance(error, RuntimeError) else "ทำรายการ Vercel ไม่สำเร็จ", file=sys.stderr)
        sys.exit(1)
