"""
Dashboard Streamlit para visualizar dados do OpenProject.
Versão refinada (frontend): visual profissional P&B,
LOGIN exatamente no padrão do seu paint:
- Logo + Título + Subtítulo acima
- 1 único retângulo (card) centralizado (com sombra)
- dentro do card: usuário, senha e entrar
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Iterable

import hashlib
import secrets
import sqlite3
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

# Garante que o pacote `app` (backend/app) seja importável
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "backend"))

from app.config import settings
from app.openproject_api.client import OpenProjectClient
from app.transformations.normalize import normalize_records

# =============================================================================
# Config (Streamlit)
# =============================================================================
st.set_page_config(
    page_title="Gestão de Projetos | Dashboard",
    page_icon="📌",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# CSS (Dashboard + Login)
# =============================================================================
st.markdown(
    """
<style>
/* ===== base ===== */
:root {
  --bg: #ffffff;
  --text: #0f172a;
  --muted: #475569;
  --border: #e5e7eb;
  --input-border: #cbd5e1;
  --input-border-focus: #94a3b8;
  --shadow: 0 18px 50px rgba(2, 6, 23, 0.10);
  --shadow-soft: 0 10px 30px rgba(2, 6, 23, 0.08);

  /* login tuneables */
  --login-card-width: 440px;
  --login-card-min-height: 420px;
  --login-card-padding-y: 42px;
  --login-card-padding-x: 34px;

  --login-field-width: 280px;
  --login-control-height: 48px;
  --login-control-font-size: 14px;
  --login-control-padding: 10px 14px;

  --login-column-max-width: 860px;
  --radius: 16px;
  --radius-sm: 12px;

  /* dashboard cards */
  --card-bg: #ffffff;
  --card-border: #e2e8f0;
  --card-shadow: 0 10px 30px rgba(2, 6, 23, 0.08);
}

/* fundo */
.main {
  background: var(--bg) !important;
}

section.main .block-container {
  max-width: none !important;
  padding-top: 0 !important;
  padding-bottom: 0 !important;
}

/* remove padding extra que o Streamlit adiciona ao topo do main */
div[data-testid="stMainBlockContainer"] {
  padding-top: 0 !important;
  padding-bottom: 0 !important;
  min-height: 100vh !important;
}

/* remove "Press Enter to submit" */
div[data-testid="InputInstructions"] {
  display: none !important;
}

div[data-testid="InputInstructions"] * {
  display: none !important;
}

/* esconder UI do Streamlit */
header[data-testid="stHeader"],
div[data-testid="stToolbar"],
div[data-testid="stAppToolbar"] {
  display: none !important;
  height: 0 !important;
}

/* coluna central do login */
.st-key-login_center_column {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  max-width: 100%;
  margin: 0 auto;
}

/* wrap */
.login-ajuste {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

/* header (logo + título) */
.login-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 18px;
  margin-bottom: 22px;
  width: min(var(--login-column-max-width), 94vw);
  text-align: center;
  font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif;
}

.login-logo {
  width: 150px;
  height: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 auto;
  background: transparent;
  filter: drop-shadow(0 6px 14px rgba(2,6,23,.12));
}

.login-logo img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  display: block;
}

.login-title {
  margin: 0;
  color: var(--text);
  font-size: 30px;
  font-weight: 900;
  line-height: 1.05;
  letter-spacing: 0.6px;
  text-transform: uppercase;
  white-space: nowrap;
}

.stVerticalBlock{
  display: flex; 
  justify-content: center; 
  align-items: center; 
}

@media (max-width: 720px) {
  .login-title {
    white-space: normal;
    font-size: 26px;
  }
  .login-logo {
    width: 120px;
    height: 120px;
  }
}

.login-subtitle {
  margin-top: 6px;
  color: var(--muted);
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.2px;
}

/* ===== Dashboard Cards ===== */
.block-card {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 14px;
  padding: 16px 18px;
  box-shadow: var(--card-shadow);
  margin-bottom: 18px;
}

.small-muted {
  color: #64748b;
  font-size: 0.92rem;
}

/* ===== CARD (1 retângulo central) ===== */
.st-key-login_card_container {
  width: var(--login-card-width) !important;
  min-height: var(--login-card-min-height) !important;
  height: auto !important;
  display: grid !important;
  place-items: center !important;
  padding: var(--login-card-padding-y) var(--login-card-padding-x) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  background: #fff !important;
  box-shadow: var(--shadow) !important;
  margin-left: auto !important;
  margin-right: auto !important;
  text-align: center !important;
}

/* ===== [CENTRALIZAÇÃO CORRETA DO BLOCO ROXO] ===== */

/* 1) seu wrapper (st.container key=login_form_wrapper) */
.st-key-login_form_wrapper {
  width: 100% !important;
  display: flex !important;
  justify-content: center !important;
  align-items: center !important;
}

/* 2) o stForm NÃO pode ocupar 100% (isso é o que puxa pra esquerda) */
.st-key-login_form_wrapper div[data-testid="stForm"] {
  border: none !important;
  padding: 0 !important;
  background: transparent !important;

  width: fit-content !important;     /* ✅ chave */
  max-width: 100% !important;
  margin-left: auto !important;
  margin-right: auto !important;
}

/* 3) garante que o form tenha exatamente a largura desejada */
.st-key-login_form_wrapper div[data-testid="stForm"] form {
  width: var(--login-field-width) !important;
  margin: 0 auto !important;
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  row-gap: 40px !important;
}

/* 4) cada “widget container” ocupa 100% */
.st-key-login_form_wrapper div[data-testid="stForm"] .element-container {
  width: 100% !important;
  margin: 0 auto !important;
}

/* 5) inputs */
.st-key-login_card_container div[data-testid="stTextInput"] > div {
  width: 100% !important;
}
.st-key-login_card_container div[data-testid="stTextInput"] input {
  width: 100% !important;
  text-align: center;
  height: var(--login-control-height);
  font-size: var(--login-control-font-size);
  font-weight: 700;
  border-radius: var(--radius-sm);
}

/* 6) botão com mesma largura */
.st-key-login_card_container div[data-testid="stFormSubmitButton"] {
  width: var(--login-field-width) !important;
  margin: 0 auto !important;
}

.st-key-login_card_container div[data-testid="stFormSubmitButton"] button {
  width: 100% !important;
  height: var(--login-control-height);
  border: 1px solid var(--input-border);
  border-radius: var(--radius-sm);
  background-color: #ffffff;
  color: #0f172a;
  font-size: var(--login-control-font-size);
  font-weight: 800;
  text-transform: lowercase;
  box-shadow: var(--shadow-soft);
  transition: transform .12s ease, box-shadow .12s ease, background-color .12s ease;
}

.st-key-login_card_container div[data-testid="stFormSubmitButton"] button:hover {
  transform: translateY(-1px);
  box-shadow: 0 14px 28px rgba(2, 6, 23, 0.15);
  background-color: #f1f5f9;
}

.st-key-login_card_container div[data-testid="stFormSubmitButton"] button:active {
  transform: translateY(0px);
  box-shadow: var(--shadow-soft);
  background-color: #e2e8f0;
}

/* ===== RESPONSIVO ===== */
@media (max-width: 520px) {
  :root {
    --login-card-width: 92vw;
    --login-field-width: 76vw;
  }
}

/* ===== FIX: senha centralizada mesmo com botão "visualizar" ===== */

/* Container interno do TextInput (onde ficam input + botão do olhinho) */
.st-key-login_card_container div[data-testid="stTextInput"] > div > div {
  position: relative !important;
  width: 100% !important;
}

/* Input: reserva espaço IGUAL dos dois lados, mantendo o texto no centro */
.st-key-login_card_container div[data-testid="stTextInput"] input {
  padding-inline: 44px !important; /* mesmo espaço esquerda/direita */
  text-align: center !important;
}

div[data-testid="InputInstructions"] {
  display: none !important;
}

div[data-testid="InputInstructions"] * {
  display: none !important;
}

/* Botão do olhinho: sai do fluxo e não "puxa" o input */
.st-key-login_card_container div[data-testid="stTextInput"] button {
  position: absolute !important;
  right: -12px !important;
  top: 50% !important;
  transform: translateY(-50%) !important;

  margin: 0 !important;
  height: 32px !important;
  width: 32px !important;
  min-width: 32px !important;
  padding: 0 !important;
  border: none !important;
  background: transparent !important;
  box-shadow: none !important;
}

</style>

""",
    unsafe_allow_html=True,
)


# =============================================================================
# Plotly defaults
# =============================================================================
PX_TEMPLATE = "plotly_white"


# =============================================================================
# Data structures + loaders
# =============================================================================
@dataclass(frozen=True)
class DataBundle:
    projects: pd.DataFrame
    work_packages: pd.DataFrame


def _load_from_api() -> DataBundle:
    if not settings.openproject_base_url:
        raise RuntimeError("OPENPROJECT_BASE_URL não configurada no .env")
    if not settings.openproject_api_key:
        raise RuntimeError("OPENPROJECT_API_KEY não configurada no .env")

    client = OpenProjectClient(
        base_url=settings.openproject_base_url,
        api_key=settings.openproject_api_key,
        timeout=max(10, settings.api_timeout_seconds),
    )
    projects = client.list_projects()
    work_packages = client.list_work_packages(
        filters_json=settings.openproject_work_packages_filters_json or None,
    )

    return DataBundle(
        projects=normalize_records(projects, "projects"),
        work_packages=normalize_records(work_packages, "work_packages"),
    )


def _load_from_csv_folder(folder: Path) -> DataBundle | None:
    projects_path = folder / "projects.csv"
    work_packages_path = folder / "work_packages.csv"
    if not projects_path.exists() or not work_packages_path.exists():
        return None

    projects = normalize_records(pd.read_csv(projects_path).to_dict("records"), "projects")
    work_packages = normalize_records(pd.read_csv(work_packages_path).to_dict("records"), "work_packages")
    return DataBundle(projects=projects, work_packages=work_packages)


def _safe_value_counts(df: pd.DataFrame, col: str) -> pd.DataFrame:
    if col not in df.columns or df.empty:
        return pd.DataFrame(columns=[col, "count"])
    return (
        df[col].fillna("N/A").astype(str).value_counts().reset_index(name="count").rename(columns={"index": col})
    )


STATUS_COLORS = {
    "new": "#5B8FF9",
    "open": "#5AD8A6",
    "in progress": "#5D7092",
    "on track": "#4E7FFF",
    "closed": "#6DC8EC",
    "done": "#7ADFA0",
    "resolved": "#9AE6B4",
    "rejected": "#F6BD16",
    "blocked": "#E8684A",
    "at risk": "#FF9845",
    "specified": "#5D7092",
    "in specification": "#6C6D6E",
    "to be scheduled": "#9270CA",
    "scheduled": "#2EC7C9",
    "confirmed": "#4E7FFF",
}
PRIORITY_COLORS = {
    "low": "#73D13D",
    "normal": "#5B8FF9",
    "medium": "#597EF7",
    "high": "#FAAD14",
    "immediate": "#FF7A45",
    "urgent": "#F5222D",
}


def _norm_text(value: object) -> str:
    return str(value).strip().lower() if value is not None else ""


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    raw = hex_color.strip().lstrip("#")
    if len(raw) != 6:
        return (243, 244, 246)
    return int(raw[0:2], 16), int(raw[2:4], 16), int(raw[4:6], 16)


def _best_text_color(bg_hex: str) -> str:
    r, g, b = _hex_to_rgb(bg_hex)
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    return "#111827" if luminance >= 155 else "#f8fafc"


def _status_color(value: object) -> str:
    return STATUS_COLORS.get(_norm_text(value), "#9ca3af")


def _priority_color(value: object) -> str:
    return PRIORITY_COLORS.get(_norm_text(value), "#9ca3af")


def _status_color_map(values: Iterable[object]) -> dict[str, str]:
    return {str(v): _status_color(v) for v in values}


def _priority_color_map(values: Iterable[object]) -> dict[str, str]:
    return {str(v): _priority_color(v) for v in values}


def _build_color_map(values: Iterable[object], base: dict[str, str]) -> dict[str, str]:
    palette = [
        "#5B8FF9",
        "#5AD8A6",
        "#5D7092",
        "#F6BD16",
        "#E8684A",
        "#6DC8EC",
        "#9270CA",
        "#FF9D4D",
        "#269A99",
        "#FF99C3",
        "#A4BADC",
        "#8F8F8F",
    ]
    result: dict[str, str] = {}
    i = 0
    for raw in values:
        key = str(raw)
        mapped = base.get(_norm_text(raw))
        if mapped:
            result[key] = mapped
        else:
            result[key] = palette[i % len(palette)]
            i += 1
    return result


def _style_status(value: object) -> str:
    color = _status_color(value)
    return f"background-color: {color}; color: {_best_text_color(color)}; font-weight: 600;"


def _style_priority(value: object) -> str:
    color = _priority_color(value)
    return f"background-color: {color}; color: {_best_text_color(color)}; font-weight: 600;"


def _style_done_ratio(value: object) -> str:
    try:
        ratio = float(value)
    except (TypeError, ValueError):
        ratio = -1
    if ratio < 0:
        color = "#f3f4f6"
    elif ratio < 40:
        color = "#fee2e2"
    elif ratio < 80:
        color = "#fef3c7"
    else:
        color = "#dcfce7"
    return f"background-color: {color}; color: #111827; font-weight: 600;"


def _style_late_rows(row: pd.Series) -> list[str]:
    is_late = str(row.get("is_late", "")).strip().lower() in {"true", "1"}
    bg = "#fff1f2" if is_late else "#ffffff"
    return [f"background-color: {bg};" for _ in row.index]


# =============================================================================
# Auth (SQLite)
# =============================================================================
def _auth_db_path() -> Path:
    return ROOT / "backend" / "data" / "dashboard_auth.db"


def _get_auth_connection() -> sqlite3.Connection:
    db_path = _auth_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _init_auth_db() -> None:
    with _get_auth_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS dashboard_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                password_salt TEXT NOT NULL,
                is_admin INTEGER NOT NULL DEFAULT 0,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL
            )
            """
        )


def _hash_password(password: str, salt_hex: str) -> str:
    pwd_bytes = password.encode("utf-8")
    salt_bytes = bytes.fromhex(salt_hex)
    return hashlib.pbkdf2_hmac("sha256", pwd_bytes, salt_bytes, 120_000).hex()


def _create_user(username: str, password: str, is_admin: bool = False) -> tuple[bool, str]:
    username_clean = username.strip()
    if len(username_clean) < 3:
        return False, "Usuário deve ter ao menos 3 caracteres."
    if len(password) < 6:
        return False, "Senha deve ter ao menos 6 caracteres."

    salt_hex = secrets.token_hex(16)
    password_hash = _hash_password(password, salt_hex)
    created_at = datetime.utcnow().isoformat(timespec="seconds")

    try:
        with _get_auth_connection() as conn:
            conn.execute(
                """
                INSERT INTO dashboard_users (username, password_hash, password_salt, is_admin, is_active, created_at)
                VALUES (?, ?, ?, ?, 1, ?)
                """,
                (username_clean, password_hash, salt_hex, 1 if is_admin else 0, created_at),
            )
        return True, "Usuário criado com sucesso."
    except sqlite3.IntegrityError:
        return False, "Usuário já existe."


def _count_users() -> int:
    with _get_auth_connection() as conn:
        row = conn.execute("SELECT COUNT(*) AS total FROM dashboard_users").fetchone()
    return int(row["total"]) if row else 0


def _authenticate_user(username: str, password: str) -> dict | None:
    username_clean = username.strip()
    with _get_auth_connection() as conn:
        row = conn.execute(
            """
            SELECT id, username, password_hash, password_salt, is_admin, is_active
            FROM dashboard_users
            WHERE username = ?
            """,
            (username_clean,),
        ).fetchone()

    if not row or int(row["is_active"]) != 1:
        return None

    candidate_hash = _hash_password(password, row["password_salt"])
    if not secrets.compare_digest(candidate_hash, row["password_hash"]):
        return None

    return {"id": int(row["id"]), "username": str(row["username"]), "is_admin": bool(row["is_admin"])}


def _list_users() -> list[dict]:
    with _get_auth_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, username, is_admin, is_active, created_at
            FROM dashboard_users
            ORDER BY username
            """
        ).fetchall()

    return [
        {
            "id": int(row["id"]),
            "username": str(row["username"]),
            "is_admin": bool(row["is_admin"]),
            "is_active": bool(row["is_active"]),
            "created_at": str(row["created_at"]),
        }
        for row in rows
    ]


def _is_authenticated() -> bool:
    return bool(st.session_state.get("is_authenticated", False))


# =============================================================================
# Login helpers
# =============================================================================
def _img_to_base64(path: Path) -> str:
    import base64
    return base64.b64encode(path.read_bytes()).decode("utf-8")




def _render_login_header(logo_path: Path) -> None:
    logo_html = ""
    if logo_path.exists():
        logo_html = f"<img src='data:image/png;base64,{_img_to_base64(logo_path)}' alt='Logo'/>"

    st.markdown(
        f"""
<div class="login-ajuste">
  <div class="login-header">
    <div class="login-logo">{logo_html}</div>
    <div>
      <div class="login-title">GESTÃO DE PROJETOS E PRODUTOS</div>
      <div class="login-subtitle">Acesso ao painel analítico</div>
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def _disable_password_manager_hints() -> None:
    # Evita sugestões do navegador/gerenciadores no login
    st.markdown(
        """
<script>
(() => {
  const apply = () => {
    const inputs = document.querySelectorAll('input');
    inputs.forEach((el) => {
      const type = (el.getAttribute('type') || '').toLowerCase();
      const placeholder = (el.getAttribute('placeholder') || '').toLowerCase();
      if (type === 'password' || placeholder.includes('senha')) {
        el.setAttribute('autocomplete', 'new-password');
        el.setAttribute('data-lpignore', 'true');
        el.setAttribute('data-form-type', 'other');
      }
      if (placeholder.includes('usuario')) {
        el.setAttribute('autocomplete', 'off');
        el.setAttribute('data-lpignore', 'true');
        el.setAttribute('data-form-type', 'other');
      }
      // Evita "Press Enter to submit"
      if (placeholder.includes('senha') || placeholder.includes('usuario')) {
        el.addEventListener('keydown', (ev) => {
          if (ev.key === 'Enter') {
            ev.preventDefault();
          }
        }, { passive: false });
      }
    });

    // desativa submit automático por Enter nos forms do login
    document.querySelectorAll('form').forEach((form) => {
      form.addEventListener('keydown', (ev) => {
        if (ev.key === 'Enter') {
          ev.preventDefault();
        }
      }, { passive: false });
    });
  };
  apply();
  setTimeout(apply, 300);
})();
</script>
""",
        unsafe_allow_html=True,
    )


def _require_dashboard_authentication() -> None:
    _init_auth_db()
    if _is_authenticated():
        return

    logo_path = Path(__file__).resolve().parent / "img" / "channels4_profile-removebg-preview.png"

    # colunas só para centralizar (sem estreitar demais)
    left, center, right = st.columns([1, 3, 1], vertical_alignment="center")
    with center:
        with st.container(key="login_center_column"):
            # marker mantido para compatibilidade com estrutura atual
            st.markdown("<div id='login_root'></div>", unsafe_allow_html=True)

            # header acima do card
            _render_login_header(logo_path)

            # card (container real com key para classe CSS estável)
            with st.container(key="login_card_container"):
                with st.container(key="login_form_wrapper"):
                    # fluxo inicial de admin (mantive)
                    if _count_users() == 0:
                        with st.form("bootstrap_admin_form", clear_on_submit=False):
                            admin_username = st.text_input("admin_u", placeholder="usuario", label_visibility="collapsed")
                            admin_password = st.text_input("admin_p", type="password", placeholder="senha", label_visibility="collapsed")
                            admin_password_confirm = st.text_input("admin_pc", type="password", placeholder="confirmar senha", label_visibility="collapsed")
                            submitted_admin = st.form_submit_button("entrar", use_container_width=False)

                        if submitted_admin:
                            if admin_password != admin_password_confirm:
                                st.error("As senhas não conferem.")
                            else:
                                created, msg = _create_user(admin_username, admin_password, is_admin=True)
                                if created:
                                    st.success("Administrador criado. Faça login para continuar.")
                                    st.rerun()
                                else:
                                    st.error(msg)

                        st.stop()

                    # login normal
                    with st.form("login_form", clear_on_submit=False):
                        username = st.text_input("u", placeholder="usuario", label_visibility="collapsed")
                        password = st.text_input("p", type="password", placeholder="senha", label_visibility="collapsed")
                        submitted_login = st.form_submit_button("entrar", use_container_width=False)

                    _disable_password_manager_hints()

                    if submitted_login:
                        user = _authenticate_user(username, password)
                        if user:
                            st.session_state["is_authenticated"] = True
                            st.session_state["authenticated_user_id"] = user["id"]
                            st.session_state["authenticated_username"] = user["username"]
                            st.session_state["authenticated_is_admin"] = user["is_admin"]
                            st.rerun()
                        st.error("Usuário ou senha inválidos.")

                    st.stop()



# =============================================================================
# Dashboard UI
# =============================================================================
def _render_header() -> None:
    col1, col2 = st.columns([3, 1], vertical_alignment="center")
    with col1:
        st.title("Painel de Controle de Projetos")
        st.markdown(
            "<div class='small-muted'>Acompanhamento de entregas, prazos e produtividade.</div>",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"<div style='text-align:right;color:#6b7280;font-size:0.95rem;'>Atualizado em: {date.today().strftime('%d/%m/%Y')}</div>",
            unsafe_allow_html=True,
        )
    st.divider()


def _render_kpis(bundle: DataBundle) -> None:
    df = bundle.work_packages

    total_projects = bundle.projects["project_id"].nunique() if not bundle.projects.empty and "project_id" in bundle.projects.columns else 0
    total_wps = df["wp_id"].nunique() if not df.empty and "wp_id" in df.columns else 0

    closed_statuses = {"Closed", "Rejected", "Concluído", "Finalizado"}
    if not df.empty:
        done_ratio_num = pd.to_numeric(df.get("done_ratio", pd.Series(dtype=float)), errors="coerce").fillna(0)
        wp_status = df.get("wp_status", pd.Series(dtype=str)).fillna("").astype(str)
        is_closed = (done_ratio_num >= 100) | (wp_status.isin(closed_statuses))
        completed_wps = int(is_closed.sum())
        late_wps = int(df["is_late"].sum()) if "is_late" in df.columns else 0
    else:
        completed_wps = 0
        late_wps = 0

    open_wps = max(0, total_wps - completed_wps)

    if not df.empty and "done_ratio" in df.columns:
        avg_completion = pd.to_numeric(df["done_ratio"], errors="coerce").mean()
        avg_completion = 0 if pd.isna(avg_completion) else float(avg_completion)
    else:
        avg_completion = 0.0

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric("Total de Projetos", total_projects)
    with c2:
        st.metric("Work Packages", total_wps)
    with c3:
        st.metric("Em Aberto", open_wps)
    with c4:
        st.metric("Atrasados", late_wps, delta=(str(late_wps) if late_wps > 0 else None), delta_color="inverse")
    with c5:
        st.metric("Progresso Médio", f"{avg_completion:.1f}%")


def _render_distribution_charts(bundle: DataBundle) -> None:
    df = bundle.work_packages
    if df.empty:
        st.warning("Sem dados para exibir gráficos de distribuição.")
        return

    col1, col2 = st.columns(2, vertical_alignment="top")

    with col1:
        st.markdown("<div class='block-card'>", unsafe_allow_html=True)
        st.markdown("#### Distribuição por Status")
        status_df = _safe_value_counts(df, "wp_status")
        fig_status = px.pie(
            status_df,
            values="count",
            names="wp_status",
            hole=0.5,
            template=PX_TEMPLATE,
            color="wp_status",
            color_discrete_map=_build_color_map(status_df["wp_status"].tolist(), STATUS_COLORS),
        )
        fig_status.update_traces(textposition="inside", textinfo="percent")
        fig_status.update_layout(showlegend=True, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_status, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='block-card'>", unsafe_allow_html=True)
        st.markdown("#### Volume por Prioridade")
        priority_df = _safe_value_counts(df, "wp_priority")
        fig_priority = px.bar(
            priority_df,
            x="wp_priority",
            y="count",
            template=PX_TEMPLATE,
            color="wp_priority",
            color_discrete_map=_build_color_map(priority_df["wp_priority"].tolist(), PRIORITY_COLORS),
        )
        fig_priority.update_layout(xaxis_title="", yaxis_title="Quantidade", showlegend=False, margin=dict(t=10, b=0, l=0, r=0))
        st.plotly_chart(fig_priority, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)


def _first_existing(columns: Iterable[str], candidates: Iterable[str]) -> str | None:
    cols = {c for c in columns}
    for c in candidates:
        if c in cols:
            return c
    return None


def _coerce_datetime(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce")


def _build_gantt_df(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    start_col = _first_existing(
        df.columns,
        ["wp_start_date", "start_date", "start", "created_at"],
    )
    end_col = _first_existing(
        df.columns,
        ["wp_due_date", "due_date", "finish_date", "end_date"],
    )
    name_col = _first_existing(
        df.columns,
        ["wp_subject", "subject", "title", "name"],
    )
    status_col = _first_existing(
        df.columns,
        ["wp_status", "status"],
    )
    project_col = _first_existing(
        df.columns,
        ["project_name", "project"],
    )
    assignee_col = _first_existing(
        df.columns,
        ["assignee", "assigned_to", "responsible", "wp_assignee"],
    )
    progress_col = _first_existing(
        df.columns,
        ["done_ratio", "progress"],
    )

    if not start_col or not end_col or not name_col:
        return pd.DataFrame()

    gantt = df.copy()
    gantt["start"] = _coerce_datetime(gantt[start_col])
    gantt["end"] = _coerce_datetime(gantt[end_col])

    gantt = gantt.dropna(subset=["start", "end"])
    gantt = gantt[gantt["end"] >= gantt["start"]]

    gantt["task"] = gantt[name_col].astype(str)
    gantt["status"] = gantt[status_col].astype(str) if status_col else "N/A"
    gantt["project"] = gantt[project_col].astype(str) if project_col else "N/A"
    gantt["assignee"] = gantt[assignee_col].astype(str) if assignee_col else "N/A"
    gantt["progress"] = pd.to_numeric(gantt[progress_col], errors="coerce").fillna(0) if progress_col else 0

    return gantt[["task", "start", "end", "status", "project", "assignee", "progress"]]


def _render_gantt(bundle: DataBundle) -> None:
    df = _build_gantt_df(bundle.work_packages)
    if df.empty:
        st.info("Sem dados suficientes para o Gantt (precisa de datas de início e fim).")
        return

    st.markdown("<div class='block-card'>", unsafe_allow_html=True)
    st.markdown("#### Gantt de Work Packages")

    fig = px.timeline(
        df,
        x_start="start",
        x_end="end",
        y="task",
        color="status",
        color_discrete_map=_status_color_map(df["status"].unique().tolist()),
        hover_data={
            "project": True,
            "assignee": True,
            "progress": True,
            "start": True,
            "end": True,
        },
    )
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(height=520, margin=dict(t=10, b=10, l=10, r=10))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


def _compute_late_df(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    late_col = "is_late" if "is_late" in df.columns else None
    due_col = _first_existing(df.columns, ["wp_due_date", "due_date", "finish_date", "end_date"])
    status_col = _first_existing(df.columns, ["wp_status", "status"])
    progress_col = _first_existing(df.columns, ["done_ratio", "progress"])

    today = pd.Timestamp(date.today())
    df2 = df.copy()

    if late_col:
        mask = df2[late_col].astype(str).str.lower().isin({"true", "1"})
    elif due_col:
        due = _coerce_datetime(df2[due_col])
        progress = pd.to_numeric(df2[progress_col], errors="coerce").fillna(0) if progress_col else 0
        status = df2[status_col].astype(str).str.lower() if status_col else ""
        closed = status.isin({"closed", "done", "resolved", "finalizado", "concluído"})
        mask = (due < today) & (~closed) & (progress < 100)
    else:
        return pd.DataFrame()

    return df2[mask]


def _render_tables(bundle: DataBundle) -> None:
    df = bundle.work_packages
    if df.empty:
        st.warning("Sem dados para tabelas.")
        return

    name_col = _first_existing(df.columns, ["wp_subject", "subject", "title", "name"])
    project_col = _first_existing(df.columns, ["project_name", "project"])
    assignee_col = _first_existing(df.columns, ["assignee", "assigned_to", "responsible", "wp_assignee"])
    status_col = _first_existing(df.columns, ["wp_status", "status"])
    priority_col = _first_existing(df.columns, ["wp_priority", "priority"])
    start_col = _first_existing(df.columns, ["wp_start_date", "start_date", "start", "created_at"])
    due_col = _first_existing(df.columns, ["wp_due_date", "due_date", "finish_date", "end_date"])
    progress_col = _first_existing(df.columns, ["done_ratio", "progress"])

    cols = [c for c in [name_col, project_col, assignee_col, status_col, priority_col, start_col, due_col, progress_col] if c]
    table = df[cols].copy()

    table = table.rename(
        columns={
            name_col: "tarefa",
            project_col: "projeto",
            assignee_col: "responsavel",
            status_col: "status",
            priority_col: "prioridade",
            start_col: "inicio",
            due_col: "fim",
            progress_col: "progresso",
        }
    )

    late_df = _compute_late_df(df)
    if not late_df.empty:
        late_table = late_df[cols].copy().rename(
            columns={
                name_col: "tarefa",
                project_col: "projeto",
                assignee_col: "responsavel",
                status_col: "status",
                priority_col: "prioridade",
                start_col: "inicio",
                due_col: "fim",
                progress_col: "progresso",
            }
        )
    else:
        late_table = pd.DataFrame()

    st.markdown("<div class='block-card'>", unsafe_allow_html=True)
    st.markdown("#### Planilha de Itens")
    view_mode = st.radio("Exibir", ["Todos os itens", "Atrasados"], horizontal=True, index=0)
    if view_mode == "Atrasados":
        if late_table.empty:
            st.info("Nenhum item atrasado.")
        else:
            st.dataframe(late_table, use_container_width=True, hide_index=True)
    else:
        st.dataframe(table, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)


def _apply_filters(
    bundle: DataBundle,
    project_filter: Iterable[str],
    status_filter: Iterable[str],
    priority_filter: Iterable[str],
) -> DataBundle:
    wps = bundle.work_packages.copy()
    if project_filter and "project_name" in wps.columns:
        wps = wps[wps["project_name"].isin(project_filter)]
    if status_filter and "wp_status" in wps.columns:
        wps = wps[wps["wp_status"].isin(status_filter)]
    if priority_filter and "wp_priority" in wps.columns:
        wps = wps[wps["wp_priority"].isin(priority_filter)]
    return DataBundle(projects=bundle.projects, work_packages=wps)


def main() -> None:
    _require_dashboard_authentication()

    # Sidebar + dados
    with st.sidebar:
        st.header("Configurações")
        st.caption(f"Usuário: {st.session_state.get('authenticated_username', '-')}")
        if st.button("Sair", use_container_width=True):
            st.session_state["is_authenticated"] = False
            st.session_state["authenticated_user_id"] = None
            st.session_state["authenticated_username"] = ""
            st.session_state["authenticated_is_admin"] = False
            st.rerun()
        st.divider()

        if st.session_state.get("authenticated_is_admin", False):
            st.subheader("Usuários")
            with st.form("create_user_form", clear_on_submit=True):
                new_username = st.text_input("Novo usuário")
                new_password = st.text_input("Nova senha", type="password")
                new_is_admin = st.checkbox("Administrador", value=False)
                submitted_user = st.form_submit_button("Criar usuário", use_container_width=True)
            if submitted_user:
                created, msg = _create_user(new_username, new_password, is_admin=new_is_admin)
                st.success(msg) if created else st.error(msg)

            users_df = pd.DataFrame(_list_users())
            if not users_df.empty:
                users_df = users_df.rename(
                    columns={"username": "usuario", "is_admin": "admin", "is_active": "ativo", "created_at": "criado_em"}
                )
                st.dataframe(users_df[["usuario", "admin", "ativo", "criado_em"]], use_container_width=True, hide_index=True)
            st.divider()

        data_mode = st.radio("Fonte de Dados", ["API (Tempo Real)", "CSV Local"], index=1)

        if data_mode == "CSV Local":
            data_folder = st.text_input("Pasta dos Dados", str(ROOT / "backend" / "data"))
            loaded = _load_from_csv_folder(Path(data_folder))
            if loaded is None:
                st.error("Arquivos CSV não encontrados.")
                st.stop()
            bundle = loaded
        else:
            try:
                with st.spinner("Conectando à API..."):
                    bundle = _load_from_api()
            except Exception as exc:
                st.error(f"Erro na API: {exc}")
                st.stop()

        st.divider()
        st.header("Filtros")
        wp_df = bundle.work_packages

        project_options = sorted(wp_df["project_name"].dropna().unique().tolist()) if "project_name" in wp_df.columns else []
        status_options = sorted(wp_df["wp_status"].dropna().unique().tolist()) if "wp_status" in wp_df.columns else []
        priority_options = sorted(wp_df["wp_priority"].dropna().unique().tolist()) if "wp_priority" in wp_df.columns else []

        project_filter = st.multiselect("Projetos", project_options)
        status_filter = st.multiselect("Status", status_options)
        priority_filter = st.multiselect("Prioridade", priority_options)

    filtered = _apply_filters(bundle, project_filter, status_filter, priority_filter)

    _render_header()
    _render_kpis(filtered)
    st.markdown("---")
    _render_distribution_charts(filtered)
    _render_gantt(filtered)
    _render_tables(filtered)


if __name__ == "__main__":
    main()
