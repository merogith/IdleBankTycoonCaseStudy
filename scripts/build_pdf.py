"""Render generated HTML over localhost and record artifact freshness hashes."""
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from threading import Thread
import hashlib
import json
import shutil

from playwright.sync_api import sync_playwright
from model import ROOT


def artifact_paths():
    return ["model-inputs.json", "case-study.template.html", "README.template.md",
            "scripts/model.py", "scripts/build_model.py", "scripts/build_pdf.py", "requirements-build.txt",
            "index.html", "README.md", "style.css", "fonts.css",
            "Idle_Bank_Tycoon_Economy_Model.xlsx", "docs/model-metrics.json", "docs/case-study.pdf",
            *[str(p.relative_to(ROOT)) for p in sorted((ROOT / "charts").glob("*.png"))]]


def main():
    server=ThreadingHTTPServer(("127.0.0.1",0),partial(SimpleHTTPRequestHandler,directory=str(ROOT)))
    Thread(target=server.serve_forever,daemon=True).start()
    try:
        with sync_playwright() as p:
            executable = shutil.which("chromium") or shutil.which("google-chrome")
            browser=p.chromium.launch(executable_path=executable,headless=True)
            page=browser.new_page()
            page.goto(f"http://127.0.0.1:{server.server_port}/index.html",wait_until="networkidle")
            page.evaluate("document.fonts.ready")
            assert page.locator("img").evaluate_all("els => els.every(x => x.complete && x.naturalWidth > 0)")
            page.pdf(path=str(ROOT/"docs/case-study.pdf"),format="A4",print_background=True,
                     margin={"top":"14mm","bottom":"16mm","left":"14mm","right":"14mm"})
            browser.close()
    finally:server.shutdown()
    manifest={path:hashlib.sha256((ROOT/path).read_bytes()).hexdigest() for path in artifact_paths()}
    (ROOT/"docs/build-manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print("Rendered docs/case-study.pdf; recorded hashes for source and published artifacts")


if __name__=="__main__":main()
