# backend/app/main.py
"""
Ponto de entrada do app.

Exemplos:
  cd backend
  python -m app.main --mode api
"""

from __future__ import annotations

import argparse

from app.logging_setup import setup_logging
from app.orchestration.run_api import run_api


def parse_args() -> argparse.Namespace:
    """Parseia argumentos de linha de comando."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=["api"],
        default="api",
        help="Modo de execucao (atualmente apenas 'api').",
    )
    return parser.parse_args()


def main() -> None:
    """Inicializa logging e executa o fluxo selecionado."""
    logger = setup_logging()
    args = parse_args()

    logger.info("Iniciando app no modo: %s", args.mode)

    if args.mode == "api":
        run_api()


if __name__ == "__main__":
    main()
