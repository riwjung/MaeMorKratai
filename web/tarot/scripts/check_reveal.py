"""Browser regression for the generated deck and reversible magical reveal.

Run against the production export already served locally. No production entropy
or app source is modified: forced draws exist only in these isolated QA pages.

    .venv/bin/python scripts/check_reveal.py /private/tmp/mmkt-reveal-qa
    MMKT_TEST_URL=http://127.0.0.1:3010 ...
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sys
import time
import traceback
from urllib.parse import urlparse

from playwright.sync_api import Page, expect, sync_playwright


ROOT = Path(__file__).resolve().parents[1]
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "/private/tmp/mmkt-reveal-qa")
URL = os.environ.get("MMKT_TEST_URL", "http://127.0.0.1:3010").rstrip("/")
ORIGIN = urlparse(URL).netloc
CARDS = json.loads((ROOT / "lib/cards.json").read_text())
MANIFEST = json.loads((ROOT / "public/cards/manifest.json").read_text())
CONTEXTS = ["คนโสด", "แอบชอบ", "คุยกัน", "ซับซ้อน", "มีแฟน", "เลิกกัน"]
CLOSE = "ปิดไพ่และเก็บกลับ"
REOPEN = "เปิดไพ่ใบเดิมจากมือแม่หมอ"
DETAILS = "อ่านความหมายทั้งหมดด้านล่าง"
OUT.mkdir(parents=True, exist_ok=True)
report = {
    "passed": False, "url": URL, "browser_channel": os.environ.get("MMKT_BROWSER_CHANNEL", "chromium-headless-shell"), "checks": [], "assets": [],
    "browser_errors": [], "bad_responses": [], "failed_requests": [],
    "external_requests": [], "screenshots": [],
    "entropy_override": "Only isolated QA pages, never app source or build",
}


def record(name: str, **data):
    report["checks"].append({"name": name, "passed": True, **data})


def screenshot(page: Page, name: str, full_page=False):
    path = OUT / (name + ".png")
    page.screenshot(path=str(path), full_page=full_page, animations="disabled")
    report["screenshots"].append(path.name)


def attach(page: Page):
    page.on("pageerror", lambda error: report["browser_errors"].append(str(error)))
    page.on("response", lambda response: report["bad_responses"].append(
        {"status": response.status, "url": response.url}) if response.status >= 400 else None)
    page.on("requestfailed", lambda request: report["failed_requests"].append(
        {"url": request.url, "error": request.failure})
        if request.failure and "ERR_ABORTED" not in request.failure else None)

    def local_only(route):
        target = urlparse(route.request.url)
        if target.scheme in ("http", "https") and target.netloc != ORIGIN:
            report["external_requests"].append(route.request.url)
            route.abort()
        else:
            route.continue_()

    page.route("**/*", local_only)
    # Count only calls made after installation. Reopening must not sample again.
    page.add_init_script("""(() => {
      window.__qaIndex = 0; window.__qaEntropyCalls = 0;
      crypto.getRandomValues = (array) => {
        window.__qaEntropyCalls += 1;
        array.fill(0); array[0] = window.__qaIndex;
        return array;
      };
    })();""")


def open_page(browser, width=1440, height=1000, reduced="reduce"):
    context = browser.new_context(viewport={"width": width, "height": height}, reduced_motion=reduced)
    page = context.new_page()
    attach(page)
    page.goto(URL, wait_until="networkidle")
    expect(page.locator(".draw-button")).to_be_enabled(timeout=10000)
    expect(page.locator(".gallery-card")).to_have_count(5)
    assert_no_overflow(page)
    return context, page


def assert_no_overflow(page: Page):
    dimensions = page.evaluate("""() => ({
      viewport: innerWidth, document: document.documentElement.scrollWidth,
      body: document.body.scrollWidth
    })""")
    assert dimensions["document"] <= dimensions["viewport"] + 1, dimensions
    assert dimensions["body"] <= dimensions["viewport"] + 1, dimensions
    return dimensions


def force_draw(page: Page, index: int, context="คนโสด", timeout=14000):
    page.locator("#context").select_option(context)
    page.evaluate("i => { window.__qaIndex = i; }", index)
    page.locator(".draw-button").click()
    wait_reveal(page, CARDS[index], context, timeout)


def wait_reveal(page: Page, card: dict, context: str, timeout=14000):
    layer = page.locator(".reveal-layer")
    expect(layer).to_have_attribute("data-card-id", card["id"], timeout=timeout)
    expect(layer).to_have_attribute("data-state", "open", timeout=4000)
    expect(page.locator("#reveal-title")).to_have_text(card["name"])
    expect(page.locator("#reveal-meaning")).to_have_text(card["meanings"][context])
    image = page.locator(".reveal-front img")
    expect(image).to_have_attribute("src", "/cards/" + card["id"] + ".jpeg")
    assert image.evaluate("e => e.complete && e.naturalWidth === 1632 && e.naturalHeight === 2624")
    expect(page.locator("#reading-details")).to_have_attribute("data-card-id", card["id"])
    expect(page.locator("#reading-details .meaning")).to_have_text(card["meanings"][context])
    # All readings remain rendered beneath the modal, including non-selected contexts.
    expected = list(card["meanings"].values())
    assert page.locator(".reading-full dd").all_text_contents() == expected
    hand_image = page.frame_locator(".room-window iframe").locator("#card-front image")
    assert hand_image.get_attribute("href").endswith("/cards/" + card["id"] + ".jpeg")
    assert page.locator("main").evaluate("e => e.inert")
    assert page.evaluate("getComputedStyle(document.body).overflow") == "hidden"
    assert_no_overflow(page)


def assert_stowed(page: Page, card: dict):
    expect(page.locator(".reveal-layer")).to_have_count(0, timeout=4000)
    frame = page.frame_locator(".room-window iframe")
    expect(frame.locator("#show-card")).to_have_css("visibility", "visible")
    # Once drawn, the card stays face up in her hand (owner's request, 2026-10-17).
    expect(frame.locator("#card-back")).to_have_css("opacity", "0")
    expect(frame.locator("#card-front")).to_have_css("opacity", "1")
    # ...and the card in the reading below shows its face, not its back.
    expect(page.locator(".result-art img.result-card-face")).to_have_attribute("src", "/cards/" + card["id"] + ".jpeg")
    assert not page.locator(".result-art .shared-card-back").count()
    expect(page.locator("#reading-details")).to_have_attribute("data-card-id", card["id"])
    assert not page.locator("main").evaluate("e => e.inert")
    assert page.evaluate("getComputedStyle(document.body).overflow") != "hidden"
    assert page.locator(".reading-full dd").all_text_contents() == list(card["meanings"].values())


def close_card(page: Page, card: dict, method="button"):
    if method == "escape":
        page.keyboard.press("Escape")
    elif method == "backdrop":
        page.locator(".reveal-veil").click(position={"x": 3, "y": 3})
    elif method == "details":
        page.get_by_role("button", name=DETAILS).click()
    else:
        page.get_by_role("button", name=CLOSE, exact=True).click()
    assert_stowed(page, card)


def assert_focus_trap(page: Page):
    close = page.get_by_role("button", name=CLOSE, exact=True)
    details = page.get_by_role("button", name=DETAILS)
    close.focus()
    page.keyboard.press("Shift+Tab")
    expect(details).to_be_focused()
    page.keyboard.press("Tab")
    expect(close).to_be_focused()
    # Repeated forward tabs must never escape into the disabled background.
    for _ in range(5):
        page.keyboard.press("Tab")
        assert page.evaluate("!!document.activeElement.closest('.reveal-panel')")


def assert_reopen(page: Page, card: dict, context: str, method="stage"):
    calls = page.evaluate("window.__qaEntropyCalls")
    if method == "stage":
        page.get_by_role("button", name=REOPEN, exact=True).click()
    elif method == "hand":
        page.locator(".hand-card-toggle").click()
    else:
        page.locator(".result-card-toggle").click()
    wait_reveal(page, card, context)
    assert page.evaluate("window.__qaEntropyCalls") == calls, "Reopening resampled a card"


def check_assets(context):
    assert len(MANIFEST["cards"]) == len(CARDS) == 5
    assert {c["id"] for c in MANIFEST["cards"]} == {c["id"] for c in CARDS}
    original_root = ROOT.parents[1] / "wiki/Images/Cards"
    for item in MANIFEST["cards"]:
        local = ROOT / "public" / item["src"].lstrip("/")
        assert hashlib.sha256(local.read_bytes()).hexdigest() == item["sha256"]
        original = original_root / item["original_filename"]
        if original.exists():
            assert hashlib.sha256(original.read_bytes()).hexdigest() == item["sha256"]
        response = context.request.get(URL + item["src"])
        assert response.ok, (item["id"], response.status)
        assert hashlib.sha256(response.body()).hexdigest() == item["sha256"]
        report["assets"].append({"id": item["id"], "sha256": item["sha256"],
                                 "served_matches_manifest": True, "original_checked": original.exists()})
    record("five_generated_jpegs_byte_identical_to_manifest")


def desktop(browser):
    context, page = open_page(browser, reduced="no-preference")
    check_assets(context)
    screenshot(page, "desktop-before", True)
    card = CARDS[2]
    started = time.monotonic()
    force_draw(page, 2, "มีแฟน")
    elapsed = time.monotonic() - started
    assert elapsed >= 5, "Normal-motion draw skipped the shuffle sequence"
    assert_focus_trap(page)
    screenshot(page, "desktop-reveal")
    before = page.locator(".reveal-card-shell").evaluate("e => getComputedStyle(e).transform")
    page.get_by_role("button", name=CLOSE, exact=True).click()
    expect(page.locator(".reveal-layer")).to_have_attribute("data-state", "closing")
    # Wait for an actual rendered animation frame; fixed 160ms is flaky under CPU-heavy Chromium.
    page.wait_for_function("before => {const e=document.querySelector('.reveal-card-shell');return e && getComputedStyle(e).transform!==before}", arg=before,timeout=1800)
    # The card flies back to her hand face up; it no longer turns to its back (owner's request, 2026-10-17).
    faces = page.locator(".reveal-flipper").evaluate("f => [getComputedStyle(f.querySelector('.reveal-front')).visibility, getComputedStyle(f.querySelector('.reveal-back')).visibility]")
    assert faces == ["visible", "hidden"], f"Close turned the card: {faces}"
    screenshot(page, "desktop-returning")
    assert_stowed(page, card)
    assert_reopen(page, card, "มีแฟน")
    close_card(page, card, "escape")
    assert_reopen(page, card, "มีแฟน", "result")
    close_card(page, card, "backdrop")
    assert_reopen(page, card, "มีแฟน", "hand")
    close_card(page, card, "details")
    # CTA scrolls to the full reading after the card returns.
    page.wait_for_function("document.querySelector('#reading-details').getBoundingClientRect().top < 120", timeout=3000)
    screenshot(page, "desktop-full-reading", True)
    record("desktop_normal_motion_draw_flip_return_reopen_escape_backdrop_details_focus", seconds=round(elapsed, 2))
    context.close()


def all_cards_mobile(browser):
    context, page = open_page(browser, width=390, height=844)
    screenshot(page, "mobile-before", True)
    for i, card in enumerate(CARDS):
        state = CONTEXTS[i % len(CONTEXTS)]
        force_draw(page, i, state, timeout=4000)
        assert_focus_trap(page)
        screenshot(page, "mobile-" + card["id"])
        close_card(page, card)
        # Context selector updates the saved card's reading without resampling.
        calls = page.evaluate("window.__qaEntropyCalls")
        for state in CONTEXTS:
            page.locator("#context").select_option(state)
            expect(page.locator("#reading-details .meaning")).to_have_text(card["meanings"][state])
        assert page.evaluate("window.__qaEntropyCalls") == calls
        assert_reopen(page, card, CONTEXTS[-1])
        close_card(page, card, "escape")
        record("mobile_draw_readings_reopen_" + card["id"], contexts_checked=6)

    # Gallery must display the owner's generated JPEG, not the old animated SVG iframe.
    for card in CARDS:
        page.get_by_role("button", name="ดูไพ่ " + card["name"], exact=True).click()
        expect(page.locator(".card-modal")).to_be_visible()
        expect(page.locator(".card-modal iframe")).to_have_count(0)
        expect(page.locator(".card-modal .generated-card > img")).to_have_attribute(
            "src", "/cards/" + card["id"] + ".jpeg")
        assert page.locator(".card-modal dd").all_text_contents() == list(card["meanings"].values())
        page.get_by_role("button", name="ปิดรายละเอียดไพ่").focus()
        page.keyboard.press("Shift+Tab")
        expect(page.locator(".card-modal .text-link")).to_be_focused()
        page.keyboard.press("Escape")
        expect(page.locator(".card-modal")).to_have_count(0)
    record("five_gallery_generated_images_and_thirty_readings")
    assert_no_overflow(page)
    context.close()


def short_mobile(browser):
    context, page = open_page(browser, width=390, height=568)
    force_draw(page, 4, "เลิกกัน", timeout=4000)
    dimensions = page.locator(".reveal-panel").evaluate("""e => {
      const r=e.getBoundingClientRect();return {top:r.top,bottom:r.bottom,height:innerHeight,
      scrollHeight:e.scrollHeight,clientHeight:e.clientHeight,overflow:getComputedStyle(e).overflowY};
    }""")
    assert dimensions["top"] >= -1 and dimensions["bottom"] <= dimensions["height"] + 1, dimensions
    if dimensions["scrollHeight"] > dimensions["clientHeight"] + 1:
        assert dimensions["overflow"] in ("auto", "scroll"), dimensions
    screenshot(page, "short-mobile-reveal")
    close_card(page, CARDS[4], "details")
    assert_no_overflow(page)
    screenshot(page, "short-mobile-details")
    record("short_mobile_390x568_overlay_and_full_reading_fit", dimensions=dimensions)
    context.close()


def preference_changes(browser):
    context, page = open_page(browser, width=390, height=844, reduced="no-preference")
    page.evaluate("window.__qaIndex = 1")
    page.locator(".draw-button").click()
    expect(page.locator(".draw-button")).to_be_disabled()
    page.wait_for_timeout(300)
    page.emulate_media(reduced_motion="reduce")
    wait_reveal(page, CARDS[1], "คนโสด", timeout=4000)
    close_card(page, CARDS[1])
    record("reduced_motion_changed_during_shuffle_reveals_once_and_releases_busy")

    # Change preference after the reveal has mounted, while it is still animating.
    page.emulate_media(reduced_motion="no-preference")
    page.evaluate("window.__qaIndex = 3")
    page.locator(".draw-button").click()
    expect(page.locator(".reveal-layer")).to_have_attribute("data-state", "opening", timeout=12000)
    page.emulate_media(reduced_motion="reduce")
    expect(page.locator(".reveal-layer")).to_have_attribute("data-state", "open", timeout=1200)
    wait_reveal(page, CARDS[3], "คนโสด")
    # A finished reduced-motion reveal must stop moving rather than remain mid-flip.
    transform = page.locator(".reveal-flipper").evaluate("e => getComputedStyle(e).transform")
    page.wait_for_timeout(150)
    assert page.locator(".reveal-flipper").evaluate("e => getComputedStyle(e).transform") == transform
    close_card(page, CARDS[3])
    assert_reopen(page, CARDS[3], "คนโสด")
    close_card(page, CARDS[3], "backdrop")
    record("reduced_motion_changed_during_reveal_stable_and_reopenable")
    context.close()


def main():
    started = time.monotonic()
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True, channel=os.environ.get("MMKT_BROWSER_CHANNEL") or None)
            try:
                desktop(browser)
                all_cards_mobile(browser)
                short_mobile(browser)
                preference_changes(browser)
                for key in ("browser_errors", "bad_responses", "failed_requests", "external_requests"):
                    assert not report[key], (key, report[key])
                report["passed"] = True
            finally:
                if not report["passed"]:
                    for i, ctx in enumerate(browser.contexts):
                        for j, pg in enumerate(ctx.pages):
                            try:
                                screenshot(pg, f"failure-{i}-{j}")
                            except Exception:
                                pass
                browser.close()
    except Exception as error:
        report["failure"] = str(error)
        report["traceback"] = traceback.format_exc()
    finally:
        report["duration_seconds"] = round(time.monotonic() - started, 2)
        (OUT / "reveal-check.json").write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps({"passed": report["passed"], "checks": len(report["checks"]),
                      "report": str(OUT / "reveal-check.json"), "failure": report.get("failure")}, ensure_ascii=False))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
