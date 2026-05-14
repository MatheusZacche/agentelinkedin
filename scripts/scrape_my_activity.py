"""Raspa a atividade recente do proprio perfil no LinkedIn.

ESQUELETO (Phase 1). Hoje so abre o browser autenticado e navega ate
`/recent-activity/all/`. Os selectors de extracao precisam ser preenchidos
inspecionando o DOM real do LinkedIn (varia bastante e muda com frequencia).

Pattern reaproveitado do buscarv/scripts/scrape_linkedin.py:
- launch_persistent_context apontando pra `.browser_profile/`
- circuit breaker (URL/texto de challenge) antes de tentar extrair
- save-as-you-go por pagina/scroll
- mojibake fixer pra texto duplo-encoded

Uso (quando estiver pronto):
    python scripts/scrape_my_activity.py \\
        --profile-slug matheuszacche \\
        --max-scrolls 5 \\
        --output runs/<run_id>/activity.json

Saida sugerida (cada item):
    {
      "post_id": "<urn:li:activity:...>",
      "url": "https://www.linkedin.com/feed/update/...",
      "posted_at": "2026-05-12T14:00:00Z",
      "text": "...",
      "media_type": "text|image|carousel|video|article",
      "reactions": 42,
      "comments": 7,
      "shares": 1,
      "impressions": null    # so o dono ve, e nem sempre visivel no DOM
    }
"""
from __future__ import annotations

import argparse
import json
import logging
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger("scrape_my_activity")

PROFILE_DIR = Path(".browser_profile").resolve()

ABORT_URL_PATTERNS = [
    "/checkpoint/challenge",
    "/checkpoint/rm/sign-in-another-account",
    "/authwall",
    "/uas/login",
]
CHALLENGE_TEXT_PATTERNS = [
    "verificacao de seguranca",
    "security verification",
    "prove you are human",
    "confirme que voce nao e um robo",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _un_mojibake(s: str | None) -> str:
    """Desfaz mojibake UTF-8-via-Latin-1 (ex: Senior -> Senior).

    Copiado do scrape_linkedin.py do buscarv. Headless Chromium as vezes
    retorna texto duplo-encoded.
    """
    if not s or "Ã" not in s:
        return s
    try:
        candidate = s.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s
    if candidate.count("Ã") < s.count("Ã"):
        return candidate
    return s


def _check_circuit_breaker(page) -> str | None:
    """Retorna pattern_name se aborto necessario, senao None."""
    url = page.url
    for pat in ABORT_URL_PATTERNS:
        if pat in url:
            return f"url_{pat.strip('/').replace('/', '_')}"
    try:
        body_text = (page.locator("body").inner_text(timeout=2000) or "").lower()
    except Exception:
        body_text = ""
    for pat in CHALLENGE_TEXT_PATTERNS:
        if pat in body_text:
            return f"text_{pat.replace(' ', '_')[:40]}"
    return None


def _extract_posts(page) -> list[dict]:
    """TODO: extrair posts do DOM.

    Selectors candidatos (validar e atualizar — LinkedIn muda):
    - div.feed-shared-update-v2 (post container)
    - span.update-components-actor__name (autor)
    - div.update-components-text (corpo)
    - time (timestamp via attribute datetime)
    - span.social-details-social-counts__reactions-count
    - li.social-details-social-counts__comments button (count)
    """
    log.warning("_extract_posts ainda nao implementado; retornando lista vazia")
    return []


def run(profile_slug: str, max_scrolls: int, output: Path, headless: bool) -> int:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        log.error("Playwright nao instalado. Rode `pip install -r requirements.txt && playwright install chromium`")
        return 2

    if not PROFILE_DIR.exists():
        log.error("Profile %s nao existe. Rode `python scripts/setup_session.py` primeiro.", PROFILE_DIR)
        return 2

    output.parent.mkdir(parents=True, exist_ok=True)
    activity_url = f"https://www.linkedin.com/in/{profile_slug}/recent-activity/all/"

    log.info("Abrindo %s", activity_url)
    posts: list[dict] = []

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=headless,
            viewport={"width": 1280, "height": 1024},
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(activity_url, wait_until="domcontentloaded")

        time.sleep(2)
        breaker = _check_circuit_breaker(page)
        if breaker:
            log.error("Circuit breaker: %s. Aborte e refaca login.", breaker)
            ctx.close()
            return 3

        for i in range(max_scrolls):
            log.info("Scroll %d/%d", i + 1, max_scrolls)
            page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
            time.sleep(random.uniform(1.5, 3.5))

        posts = _extract_posts(page)
        ctx.close()

    payload = {
        "scraped_at": _now_iso(),
        "profile": profile_slug,
        "count": len(posts),
        "posts": posts,
    }
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    log.info("Salvo %d posts em %s", len(posts), output)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile-slug", required=True, help="Ex: matheuszacche")
    ap.add_argument("--max-scrolls", type=int, default=5)
    ap.add_argument("--output", type=Path, default=Path("runs/latest/activity.json"))
    ap.add_argument("--headless", action="store_true")
    args = ap.parse_args()
    return run(args.profile_slug, args.max_scrolls, args.output, args.headless)


if __name__ == "__main__":
    sys.exit(main())
