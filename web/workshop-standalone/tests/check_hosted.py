"""Real Supabase smoke test with temporary synthetic users; no email delivery.

Run a local Next server using credentials.py, then run this from the project root.
Only the two users created by this run and their test audio/rows are removed.
No passwords, sessions, API keys or signed URLs are written to disk or printed.
"""
import asyncio
import os
import json
import secrets
import sys
import uuid
from pathlib import Path

from playwright.async_api import async_playwright

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from passwords import request  # noqa: E402

BASE = os.environ.get("WORKSHOP_TEST_URL", "http://127.0.0.1:3012").rstrip("/")
if BASE not in ("http://127.0.0.1:3012", "https://maemorkratai-workshop.vercel.app"):
    raise RuntimeError("Use the workshop loopback or its verified production URL only")
OUT = Path(__file__).resolve().parents[1] / "artifacts"


def cleanup(users):
    for user in users:
        user_id = user["id"]
        # Only accounts this test created, with a reserved synthetic email prefix.
        actual = request(f"/auth/v1/admin/users/{user_id}")
        if actual.get("email") != user["email"] or not actual["email"].startswith("workshop-smoke-"):
            raise RuntimeError("Cleanup identity check failed")
        rows = request(f"/rest/v1/workshop_recordings?select=object_key&reader_id=eq.{user_id}")
        if rows:
            request("/storage/v1/object/workshop-audio", "DELETE",
                    {"prefixes": [r["object_key"] for r in rows]})
        request(f"/rest/v1/workshop_readings?reader_id=eq.{user_id}", "DELETE")
        request(f"/rest/v1/workshop_members?user_id=eq.{user_id}", "DELETE")
        request(f"/auth/v1/admin/users/{user_id}", "DELETE")


async def main():
    OUT.mkdir(exist_ok=True)
    journal = OUT / "hosted-test-cleanup.json"
    if journal.exists():
        raise RuntimeError("Previous test cleanup journal exists; clean those synthetic accounts first")
    users = []
    report = {"provider": "hosted Supabase", "application": BASE, "emailsSent": 0, "passed": False}
    try:
        for index in range(2):
            email = f"workshop-smoke-{uuid.uuid4().hex}@example.com"
            password = secrets.token_urlsafe(24)
            user = request("/auth/v1/admin/users", "POST",
                           {"email": email, "password": password, "email_confirm": True})
            identity = {"id": user["id"], "email": email}
            users.append(identity)
            journal.write_text(json.dumps([{"id": u["id"], "email": u["email"]} for u in users]))
            request("/rest/v1/workshop_members", "POST",
                    {"user_id": user["id"], "role": "reader", "display_name": f"ทดสอบระบบ {index + 1}", "active": True})
            identity["password"] = password  # Memory only; never update journal with this.

        async with async_playwright() as p:
            browser = await p.chromium.launch(args=["--use-fake-ui-for-media-stream", "--use-fake-device-for-media-stream"])
            ctx = await browser.new_context(viewport={"width": 390, "height": 844}, permissions=["microphone"])
            page = await ctx.new_page()
            page.set_default_timeout(30000)
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            anon = await ctx.request.get(BASE + "/api/workshop/")
            assert anon.status == 401
            await page.goto(BASE + "/login")
            await page.get_by_label("อีเมลที่ได้รับสิทธิ์").fill(users[0]["email"])
            await page.get_by_label("รหัสผ่าน", exact=True).fill("incorrect-password")
            await page.get_by_role("button", name="เข้าห้องทดลอง", exact=True).click()
            await page.get_by_role("alert").wait_for()
            await page.get_by_label("รหัสผ่าน", exact=True).fill(users[0]["password"])
            await page.get_by_role("button", name="เข้าห้องทดลอง", exact=True).click()
            await page.get_by_role("heading", name="อ่านในแบบของคุณ", exact=True).wait_for()
            await page.get_by_role("button", name="เริ่มอัดเสียง", exact=True).wait_for()
            print("PASS: hosted password sign-in, invalid-password rejection, session/membership", flush=True)

            listing = await ctx.request.get(BASE + "/api/workshop/")
            listed = (await listing.json())["cases"]
            assert len(listed) == 60 and all("cards" not in c for c in listed)
            assert {k: sum(c["category"] == k for c in listed) for k in ("love", "work", "money", "health")} == {
                "love": 30, "work": 10, "money": 10, "health": 10
            }
            # Category changes must not silently discard unsaved text.
            await page.get_by_label("คำอ่านฉบับข้อความ", exact=False).fill("ร่างที่ยังไม่ได้บันทึก")
            page.once("dialog", lambda dialog: dialog.dismiss())
            await page.get_by_role("button", name="การงาน 10 เคส", exact=True).click()
            assert await page.get_by_label("คำอ่านฉบับข้อความ", exact=False).input_value() == "ร่างที่ยังไม่ได้บันทึก"
            assert await page.get_by_role("button", name="ทุกหมวด 60 เคส", exact=True).get_attribute("aria-pressed") == "true"
            page.once("dialog", lambda dialog: dialog.accept())
            await page.get_by_role("button", name="การงาน 10 เคส", exact=True).click()
            await page.get_by_role("heading", name="ฉันควรมองโอกาสเปลี่ยนงานครั้งนี้อย่างไร?", exact=True).wait_for()

            for label, case_id, heading in [
                ("การงาน", "case-31", "ฉันควรมองโอกาสเปลี่ยนงานครั้งนี้อย่างไร?"),
                ("การเงิน", "case-41", "ฉันควรเริ่มจัดระเบียบการเงินจากตรงไหน?"),
            ]:
                await page.get_by_role("button", name=f"{label} 10 เคส", exact=True).click()
                await page.get_by_role("heading", name=heading, exact=True).wait_for()
                assert await page.locator(".scenario .category-tag").inner_text() == label
                await page.get_by_role("button", name="เปิดรายการเคส", exact=True).click()
                assert await page.locator(".case-list .case-item:visible").count() == 10
                await page.get_by_role("button", name="เปิดรายการเคส", exact=True).click()
                text = "คำตอบสมมติสำหรับตรวจหมวด" + label
                await page.get_by_label("คำอ่านฉบับข้อความ", exact=False).fill(text)
                await page.locator(".consent input").check()
                await page.get_by_role("button", name="บันทึกร่าง", exact=True).click()
                await page.get_by_role("status").filter(has_text="บันทึกร่างลงฐานข้อมูลแล้ว").wait_for()
                response = await ctx.request.get(BASE + "/api/workshop/cases/" + case_id)
                assert (await response.json())["snapshot"]["baseline"]["answer"] == text
                await page.get_by_role("button", name="เคสถัดไป", exact=False).click()
                await page.locator(".scenario .pill").filter(has_text=str(int(case_id[-2:]) + 1)).wait_for()
                await page.get_by_role("button", name="เคสก่อนหน้า", exact=False).click()
                await page.get_by_role("heading", name=heading, exact=True).wait_for()
                assert await page.get_by_label("คำอ่านฉบับข้อความ", exact=False).input_value() == text
                assert await page.get_by_role("button", name="เคสก่อนหน้า", exact=False).is_disabled()
            await page.get_by_role("button", name="สุขภาพ 10 เคส", exact=True).click()
            await page.get_by_role("heading", name="ฉันควรจัดสมดุลการพักและภาระในชีวิตอย่างไร?", exact=True).wait_for()
            assert await page.locator(".scenario .category-tag").inner_text() == "สุขภาพ"
            assert await page.locator(".category-hint").is_visible()
            await page.get_by_role("button", name="เปิดรายการเคส", exact=True).click()
            assert await page.locator(".case-list .case-item:visible").count() == 10
            await page.locator(".case-list .case-item").last.click()
            await page.get_by_role("heading", name="ฉันควรรักษากำลังใจในการดูแลตัวเองอย่างไร?", exact=True).wait_for()
            assert await page.get_by_role("button", name="เคสถัดไป", exact=False).is_disabled()
            await page.get_by_role("button", name="เปิดรายการเคส", exact=True).click()
            await page.locator(".case-list .case-item").first.click()
            await page.get_by_role("heading", name="ฉันควรจัดสมดุลการพักและภาระในชีวิตอย่างไร?", exact=True).wait_for()
            assert await page.get_by_role("button", name="เคสก่อนหน้า", exact=False).is_disabled()
            assert await page.evaluate("document.documentElement.scrollWidth<=innerWidth")
            await page.screenshot(path=str(OUT / "hosted-categories-mobile.png"), full_page=True)
            print("PASS: four categories, filtered navigation/progress, unsaved-change guard and new-case persistence", flush=True)

            async def detail():
                response = await ctx.request.get(BASE + "/api/workshop/cases/case-51")
                assert response.ok, f"Detail status {response.status}"
                return await response.json()

            before = await detail()
            assert len(before["cards"]) == 3
            await page.get_by_role("button", name="เริ่มอัดเสียง", exact=True).click()
            await page.get_by_role("button", name="หยุดอัด", exact=True).wait_for()
            await page.wait_for_timeout(1700)
            await page.get_by_role("button", name="หยุดอัด", exact=True).click()
            await page.locator(".local-take audio").wait_for()
            await page.locator(".consent input").check()
            await page.get_by_role("button", name="บันทึกร่าง", exact=True).click()
            await page.get_by_role("status").filter(has_text="บันทึกร่างลงฐานข้อมูลแล้ว").wait_for()
            saved = await detail()
            audio_id = saved["snapshot"]["baseline"]["audioId"]
            assert audio_id and len(saved["recordings"]) == 1
            audio = await ctx.request.get(BASE + "/api/workshop/audio/" + audio_id,
                                          headers={"Range": "bytes=0-31"})
            assert audio.status == 206 and len(await audio.body()) == 32
            await page.reload()
            await page.locator(".saved-audio audio").wait_for()
            await page.locator(".saved-audio audio").evaluate("(e)=>e.play()")
            await page.wait_for_timeout(400)
            assert await page.locator(".saved-audio audio").evaluate("(e)=>e.currentTime>0&&!e.error")
            print("PASS: hosted signed upload, audio verification, save/reload, Range/playback", flush=True)

            await page.locator(".consent input").check()
            await page.get_by_role("button", name="เก็บคำอ่าน แล้วเปิดใบที่ 4", exact=True).click()
            await page.get_by_role("heading", name="ใบขยายช่วยให้เห็นอะไรเพิ่ม?", exact=True).wait_for()
            sealed = await detail()
            assert len(sealed["cards"]) == 4 and sealed["snapshot"]["baseline"] == saved["snapshot"]["baseline"]
            await page.get_by_label("คำอ่านหลังเห็นใบขยาย", exact=False).fill("ข้อมูลทดสอบระบบชั่วคราว ไม่ใช่คำอ่านจริง")
            await page.get_by_role("button", name="บันทึกและส่งทบทวน", exact=True).click()
            await page.get_by_role("heading", name="เก็บเคสนี้เรียบร้อยแล้ว", exact=True).wait_for()
            assert (await detail())["snapshot"]["stage"] == "review"
            assert "1 / 10" in " ".join((await page.locator(".progress-copy b").inner_text()).split())
            assert await page.evaluate("document.documentElement.scrollWidth<=innerWidth")

            other = await browser.new_context()
            op = await other.new_page()
            await op.goto(BASE + "/login")
            await op.get_by_label("อีเมลที่ได้รับสิทธิ์").fill(users[1]["email"])
            await op.get_by_label("รหัสผ่าน", exact=True).fill(users[1]["password"])
            await op.get_by_role("button", name="เข้าห้องทดลอง", exact=True).click()
            await op.get_by_role("heading", name="อ่านในแบบของคุณ", exact=True).wait_for()
            assert (await other.request.get(BASE + "/api/workshop/audio/" + audio_id)).status == 404
            assert (await other.request.get(BASE + "/api/workshop/?reader=" + users[0]["id"])).status == 403
            assert (await other.request.get(BASE + "/api/workshop/export")).status == 403
            own = await other.request.get(BASE + "/api/workshop/cases/case-51")
            assert (await own.json())["snapshot"]["revision"] == 0
            async with page.expect_response(lambda r: r.url.endswith("/api/auth/signout")) as logout_response:
                await page.get_by_role("button", name="ออกจากระบบ", exact=True).click()
            logout = await logout_response.value
            assert logout.status == 303, f"Sign-out returned {logout.status}"
            await page.wait_for_url("**/login")
            assert (await ctx.request.get(BASE + "/api/workshop/")).status == 401
            assert not errors, "Browser page errors occurred"
            print("PASS: hosted fourth-card flow, reader isolation, export denied, sign-out", flush=True)
            await page.screenshot(path=str(OUT / "hosted-login-mobile.png"), full_page=True)
            await browser.close()
            webkit = await p.webkit.launch()
            mobile = await webkit.new_context(viewport={"width": 390, "height": 844}, is_mobile=True)
            wp = await mobile.new_page()
            await wp.goto(BASE + "/login")
            await wp.get_by_label("อีเมลที่ได้รับสิทธิ์").fill(users[1]["email"])
            await wp.get_by_label("รหัสผ่าน", exact=True).fill(users[1]["password"])
            await wp.get_by_role("button", name="เข้าห้องทดลอง", exact=True).click()
            await wp.get_by_role("heading", name="อ่านในแบบของคุณ", exact=True).wait_for()
            await wp.reload()
            await wp.get_by_role("heading", name="อ่านในแบบของคุณ", exact=True).wait_for()
            for label in ["การงาน", "การเงิน", "สุขภาพ", "ความรัก"]:
                count = 30 if label == "ความรัก" else 10
                await wp.get_by_role("button", name=f"{label} {count} เคส", exact=True).click()
                await wp.locator(".scenario .category-tag").filter(has_text=label).wait_for()
            assert await wp.evaluate("document.documentElement.scrollWidth<=innerWidth")
            await wp.get_by_role("button", name="ออกจากระบบ", exact=True).click()
            await wp.wait_for_url("**/login")
            assert (await mobile.request.get(BASE + "/api/workshop/")).status == 401
            await webkit.close()
            print("PASS: hosted WebKit password sign-in, session persistence and sign-out", flush=True)
            report["passed"] = True
    finally:
        try:
            cleanup(users)
            journal.unlink(missing_ok=True)
            report["temporaryDataRemoved"] = True
            print("CLEANUP: temporary accounts, readings and audio removed", flush=True)
        finally:
            (OUT / "hosted-check.json").write_text(json.dumps(report, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
