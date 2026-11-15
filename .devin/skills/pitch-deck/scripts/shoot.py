"""Play a story through the running Espoo Work Map and capture screens for the pitch deck.

Usage:  python shoot.py <plan.json> <out_dir>
Env:    EWM_WEB (default http://127.0.0.1:5173), EWM_API (default http://127.0.0.1:8000/api)

A plan is a JSON list of steps, run in order:
  {"reset": 1}                                   POST /demo/reset (rebuilds the synthetic DB)
  {"stage": "registration", "event": "ev-..."}   move the demo clock (registration | matching_closed | live | after)
  {"api": [METHOD, path, user_email|null, body], "save": {"key": "python expr on r"}}
                                                 call the API as a demo user; saved values replace "{key}" later
  {"url": "/path", "user": "email", "name": "file", "mobile": false, "full": false,
   "click": ["text", ...], "scroll": 300, "hidebar": true,
   "parts": [{"text": "heading text", "out": "file", "exact": false}]}
                                                 open a page; "name" saves the viewport (or full page),
                                                 each "part" saves the nearest `.card` around that text
Demo users log in with password demo1234. Use 127.0.0.1, not localhost.
"""
import json, os, sys, time, urllib.error, urllib.request
from playwright.sync_api import sync_playwright

WEB = os.environ.get("EWM_WEB", "http://127.0.0.1:5173")
API = os.environ.get("EWM_API", "http://127.0.0.1:8000/api")
SAVED: dict[str, str] = {}


def call(method, path, user=None, body=None):
    headers = {"Content-Type": "application/json"}
    if user:
        headers["Authorization"] = "Bearer " + token(user)
    data = json.dumps(body).encode() if body is not None else (b"{}" if method == "POST" else None)
    req = urllib.request.Request(API + path, data=data, headers=headers, method=method)
    return json.loads(urllib.request.urlopen(req).read() or b"{}")


def token(email):
    return call("POST", "/auth/login", body={"login": email, "password": "demo1234"})["token"]


def fill(value):
    raw = json.dumps(value)
    for k, v in SAVED.items():
        raw = raw.replace("{" + k + "}", v)
    return json.loads(raw)


def main(plan_path, out):
    os.makedirs(out, exist_ok=True)
    plan = json.load(open(plan_path, encoding="utf-8"))
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome")
        for step in plan:
            if "reset" in step:
                call("POST", "/demo/reset"); time.sleep(1); print("reset"); continue
            if "stage" in step:
                call("POST", "/demo/clock", body={"stage": step["stage"], "event_id": step.get("event", "ev-2027-03")})
                print("stage", step["stage"]); continue
            if "api" in step:
                method, path, user, body = fill(step["api"])
                try:
                    r = call(method, path, user, body)
                except urllib.error.HTTPError as e:
                    print("API FAILED", method, path, e.code, e.read()[:300]); continue
                for k, expr in step.get("save", {}).items():
                    SAVED[k] = str(eval(expr, {"r": r}))
                print("api", method, path); continue

            mobile = step.get("mobile", False)
            ctx = browser.new_context(
                viewport={"width": 390, "height": 844} if mobile else {"width": 1440, "height": 900},
                device_scale_factor=2 if mobile else 1.5, locale="en-GB")
            if step.get("user"):
                t = token(step["user"])
                ctx.add_init_script(f"localStorage.setItem('ewm.token', {json.dumps(t)}); localStorage.setItem('ewm.lang','en');")
            page = ctx.new_page()
            page.goto(WEB + step["url"], wait_until="networkidle")
            page.wait_for_timeout(1200)
            for text in step.get("click", []):
                page.get_by_text(text, exact=False).first.click()
                page.wait_for_timeout(900)
            if step.get("hidebar", True):
                page.add_style_tag(content=".demo-bar{display:none!important}")
                page.wait_for_timeout(300)
            for part in step.get("parts", []):
                el = page.get_by_text(part["text"], exact=part.get("exact", False)).first
                box = el.locator("xpath=ancestor-or-self::*[contains(concat(' ',@class,' '),' card ')][1]")
                try:
                    box.scroll_into_view_if_needed(timeout=5000); page.wait_for_timeout(300)
                    box.screenshot(path=os.path.join(out, part["out"] + ".png"), timeout=5000)
                    print("part", part["out"])
                except Exception:
                    print("MISSING part", part["out"], "-", part["text"])
            if step.get("scroll"):
                page.mouse.wheel(0, step["scroll"]); page.wait_for_timeout(600)
            if step.get("name"):
                page.screenshot(path=os.path.join(out, step["name"] + ".png"), full_page=step.get("full", False))
                print("shot", step["name"])
            ctx.close()
        browser.close()


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
