"""
Setup simples de logging.

Mantem formato consistente para facilitar suporte e diagnostico.
"""

import logging


def setup_logging() -> logging.Logger:
    """Configura o logger raiz com formato padrao."""
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s %(name)s: %(message)s",
    )
    return logging.getLogger("app")
