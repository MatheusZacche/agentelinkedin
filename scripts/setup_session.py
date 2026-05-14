"""Login manual no LinkedIn pra persistir cookies no Playwright profile.

Adaptado do `setup_sessions.py` do buscarv. Aqui so faz LinkedIn, e usa um
profile separado (`.browser_profile/`) pra nao colidir com a sessao de jobs.

Uso:
    python scripts/setup_session.py

Quando a janela do Chromium abrir, faca login normalmente. Quando estiver no
feed (nao na tela de login), volte aqui e aperte Enter pra fechar e salvar.

Notas:
- Nunca rodar em headless. Login interativo so faz sentido local.
- Profile e gitignored. Se apagar `.browser_profile/`, precisa logar de novo.
- O scrape de atividade (`scripts/scrape_my_activity.py`) reusa essa sessao.
"""
from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

PROFILE_DIR = Path(".browser_profile").resolve()
LINKEDIN_FEED = "https://www.linkedin.com/feed/"


def main() -> int:
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Profile dir: {PROFILE_DIR}")
    print(f"Navegando para: {LINKEDIN_FEED}")
    print("Voce esta logado quando ver o feed (nao a tela de login).\n")

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
            viewport={"width": 1280, "height": 800},
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(LINKEDIN_FEED)

        try:
            input("  > Faca login, depois aperte Enter aqui pra confirmar: ")
        except (KeyboardInterrupt, EOFError):
            print("\n  ! Cancelado. Profile salvo do jeito que estava.")
        else:
            print(f"  OK. URL final: {page.url}")
        finally:
            ctx.close()

    print("\nDone. Proximo passo: rodar `python scripts/scrape_my_activity.py`.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
