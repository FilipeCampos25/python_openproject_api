"""
Dashboard Streamlit para visualizar dados do OpenProject.
Versão otimizada para visualização profissional e intuitiva.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Iterable

import os
import sys
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Garante que o pacote `app` (backend/app) seja importavel
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "backend"))

# Configuração de ambiente Streamlit
_streamlit_config_dir = os.environ.get("STREAMLIT_CONFIG_DIR")
_config_path = Path(_streamlit_config_dir) if _streamlit_config_dir else Path.home() / ".streamlit"

try:
    _config_path.mkdir(parents=True, exist_ok=True)
    _cred_file = _config_path / "credentials.toml"
    if not _cred_file.exists():
        _cred_file.write_text("[general]\nemail = \"\"\n")
except Exception:
    pass

import streamlit as st

from app.config import settings
from app.openproject_api.client import OpenProjectClient, OpenProjectAPIError
from app.transformations.normalize import normalize_records

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Gestão de Projetos | Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILO CSS CUSTOMIZADO ---
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    section.main .block-container {
        padding-top: 0rem;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    div[data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: bold;
        color: #1f77b4;
    }
    .stPlotlyChart {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    h1, h2, h3 {
        color: #2c3e50;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .status-card {
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 10px;
    }

    /* =========================
       HEADER (ADICIONADO)
       ========================= */
    .brand-title {
        font-family: 'Arial Black', Arial, sans-serif;
        font-size: 40px;
        color: #2c3e50;
        letter-spacing: 1px;
        text-transform: uppercase;
        text-align: center;
        width: 100%;
        line-height: 1.2;
        margin-top: 0;
        
    /* Tenta esconder a toolbar (faixa azul) com máxima prioridade */
    div[data-testid="stAppToolbar"],
    div.stAppToolbar,
    header[data-testid="stHeader"],
    div[data-testid="stToolbar"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        min-height: 0 !important;
    }

    /* Remove o espaço extra que o "chrome" deixa */
    div[data-testid="stAppViewContainer"] .main {
        padding-top: 0rem !important;
    }

    section[data-testid="stMain"] {
        padding-top: 0rem !important;
    }

    div[data-testid="stMainBlockContainer"] {
        padding-top: 0rem !important;
    }
    
    /* ajuste final agressivo: puxa a página para cima */
    div[data-testid="stAppViewContainer"] {
        margin-top: -60px !important;
    }

    </style>
    """, unsafe_allow_html=True)

@dataclass(frozen=True)
class DataBundle:
    """Agrupa dados normalizados para o dashboard."""
    projects: pd.DataFrame
    work_packages: pd.DataFrame


def _load_from_api() -> DataBundle:
    """Carrega dados diretamente da API do OpenProject."""
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
    """Carrega dados a partir de CSVs exportados pelo pipeline."""
    projects_path = folder / "projects.csv"
    work_packages_path = folder / "work_packages.csv"

    if not projects_path.exists() or not work_packages_path.exists():
        return None

    projects = normalize_records(pd.read_csv(projects_path).to_dict("records"), "projects")
    work_packages = normalize_records(
        pd.read_csv(work_packages_path).to_dict("records"),
        "work_packages",
    )
    return DataBundle(projects=projects, work_packages=work_packages)


def _safe_value_counts(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """Gera value_counts de forma segura para colunas ausentes."""
    if col not in df.columns or df.empty:
        return pd.DataFrame(columns=[col, "count"])
    return df[col].fillna("N/A").value_counts().reset_index(name="count").rename(columns={"index": col})


# ==================================================================================
# HEADER COM LOGO (ESQ) + TÍTULO CENTRAL (ADICIONADO / CORRIGIDO)
# - SEM HTML DE LAYOUT (evita aparecer tags na tela)
# - st.image resolve caminho local corretamente
# ==================================================================================
def _render_brand_header(logo_path: str = "assets/logo.png") -> None:
    """
    Header:
      - Logo à esquerda (PNG/JPG local)
      - Título central: GESTÃO DE PROJETOS E PRODUTOS
      - Fonte: Arial Black, tamanho 18
    """
    logo_file = Path(logo_path)

    with st.container():
        # 3 colunas para manter o título realmente centralizado
        col_logo, col_title, col_right = st.columns([1.2, 6, 1.2], vertical_alignment="center")

        with col_logo:
            if logo_file.exists():
                # ajuste width conforme seu gosto
                st.image(str(logo_file), width=250)
            else:
                # Se não achar a imagem, não quebra o layout
                st.write("")

        with col_title:
            st.markdown("<div class='brand-title'>GESTÃO DE PROJETOS E PRODUTOS</div>", unsafe_allow_html=True)

        with col_right:
            st.write("")

        st.divider()


def _render_header():
    """Renderiza o cabeçalho do dashboard."""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("📊 Painel de Controle de Projetos")
        st.markdown("Acompanhamento estratégico de entregas, prazos e produtividade.")
    with col2:
        st.markdown(
            f"<div style='text-align: right; color: gray; padding-top: 20px;'>Atualizado em: {date.today().strftime('%d/%m/%Y')}</div>",
            unsafe_allow_html=True
        )
    st.divider()


def _render_kpis(bundle: DataBundle):
    """Renderiza KPIs principais com visual moderno."""
    df = bundle.work_packages

    total_projects = bundle.projects["project_id"].nunique() if not bundle.projects.empty else 0
    total_wps = df["wp_id"].nunique() if not df.empty else 0

    # Cálculo de status
    late_wps = int(df["is_late"].sum()) if "is_late" in df.columns else 0

    # Consideramos "Concluído" se done_ratio for 100 ou status for 'Closed' ou 'Rejected'
    closed_statuses = ['Closed', 'Rejected', 'Concluído', 'Finalizado']
    is_closed = (df["done_ratio"].fillna(0) >= 100) | (df["wp_status"].isin(closed_statuses))
    completed_wps = int(is_closed.sum()) if not df.empty else 0
    open_wps = total_wps - completed_wps

    # Percentual de conclusão global
    # Se done_ratio estiver ausente ou todo vazio, evita NaN aparecer no KPI.
    if not df.empty and "done_ratio" in df.columns:
        avg_completion = pd.to_numeric(df["done_ratio"], errors="coerce").mean()
        if pd.isna(avg_completion):
            avg_completion = 0
    else:
        avg_completion = 0

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric("Total de Projetos", total_projects)
    with c2:
        st.metric("Work Packages", total_wps)
    with c3:
        st.metric("Em Aberto", open_wps)
    with c4:
        st.metric("Atrasados", late_wps, delta=f"{late_wps}" if late_wps > 0 else None, delta_color="inverse")
    with c5:
        st.metric("Progresso Médio", f"{avg_completion:.1f}%")


def _render_distribution_charts(bundle: DataBundle):
    """Gráficos de distribuição de status e prioridade."""
    df = bundle.work_packages
    if df.empty:
        st.warning("Sem dados para exibir gráficos de distribuição.")
        return

    col1, col2 = st.columns(2)

    with col1:
        status_df = _safe_value_counts(df, "wp_status")
        fig_status = px.pie(
            status_df,
            values="count",
            names="wp_status",
            title="<b>Distribuição por Status</b>",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig_status.update_traces(textposition='inside', textinfo='percent+label')
        fig_status.update_layout(showlegend=False, margin=dict(t=40, b=0, l=0, r=0))
        st.plotly_chart(fig_status, use_container_width=True)

    with col2:
        priority_df = _safe_value_counts(df, "wp_priority")
        # Ordenação lógica de prioridade se possível
        priority_order = ['Low', 'Normal', 'High', 'Immediate']
        priority_df['sort'] = priority_df['wp_priority'].apply(lambda x: priority_order.index(x) if x in priority_order else 99)
        priority_df = priority_df.sort_values('sort')

        fig_priority = px.bar(
            priority_df,
            x="wp_priority",
            y="count",
            title="<b>Volume por Prioridade</b>",
            color="wp_priority",
            color_discrete_map={'Low': '#2ecc71', 'Normal': '#3498db', 'High': '#f1c40f', 'Immediate': '#e74c3c'}
        )
        fig_priority.update_layout(xaxis_title="", yaxis_title="Quantidade", showlegend=False, margin=dict(t=40, b=0, l=0, r=0))
        st.plotly_chart(fig_priority, use_container_width=True)


def _render_productivity_charts(bundle: DataBundle):
    """Gráficos de produtividade e responsáveis."""
    df = bundle.work_packages
    if df.empty:
        return

    col1, col2 = st.columns([2, 1])

    with col1:
        # Evolução de criação vs atualização (se houver datas)
        st.markdown("### Cronograma de Atividades")
        _render_gantt_like(bundle)

    with col2:
        st.markdown("### Carga por Responsável")
        assignee_df = _safe_value_counts(df, "assignee")
        assignee_df = assignee_df.sort_values("count", ascending=True)
        fig_assignee = px.bar(
            assignee_df,
            y="assignee",
            x="count",
            orientation='h',
            title=None,
            color_discrete_sequence=['#1f77b4']
        )
        fig_assignee.update_layout(xaxis_title="Work Packages", yaxis_title="", margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_assignee, use_container_width=True)


def _render_gantt_like(bundle: DataBundle) -> None:
    """Renderiza uma timeline estilo Gantt aprimorada."""
    df = bundle.work_packages.copy()
    if df.empty or "start_date" not in df.columns or "due_date" not in df.columns:
        st.info("Sem datas suficientes para montar a linha do tempo.")
        return

    df["start_date"] = pd.to_datetime(df["start_date"], errors="coerce")
    df["due_date"] = pd.to_datetime(df["due_date"], errors="coerce")

    # Para o Gantt, se não tem start_date mas tem due_date, usamos due_date como start
    df["start_date"] = df["start_date"].fillna(df["due_date"])
    df["due_date"] = df["due_date"].fillna(df["start_date"])

    df = df.dropna(subset=["start_date", "due_date"])

    if df.empty:
        st.info("Sem datas suficientes para montar a linha do tempo.")
        return

    # Limitar a 20 itens para não poluir o visual, priorizando os mais recentes/relevantes
    df = df.sort_values("due_date", ascending=False).head(20)

    fig = px.timeline(
        df,
        x_start="start_date",
        x_end="due_date",
        y="wp_subject",
        color="wp_status",
        hover_data=["project_name", "assignee", "wp_priority", "done_ratio"],
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig.update_yaxes(autorange="reversed", title="")
    fig.update_layout(
        margin=dict(t=0, b=0, l=0, r=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)


def _apply_filters(bundle: DataBundle, project_filter: Iterable[str], status_filter: Iterable[str], priority_filter: Iterable[str]) -> DataBundle:
    """Aplica filtros selecionados no sidebar."""
    wps = bundle.work_packages.copy()
    if project_filter:
        wps = wps[wps["project_name"].isin(project_filter)]
    if status_filter:
        wps = wps[wps["wp_status"].isin(status_filter)]
    if priority_filter:
        wps = wps[wps["wp_priority"].isin(priority_filter)]
    return DataBundle(projects=bundle.projects, work_packages=wps)


def main() -> None:
    """Entry point do Dashboard."""
    logo_path = Path(__file__).resolve().parent / "img" / "channels4_profile-removebg-preview.png"

    # --- SIDEBAR ---
    with st.sidebar:
        st.header("⚙️ Configurações")

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
        st.header("🔍 Filtros")

        project_options = sorted(bundle.work_packages["project_name"].dropna().unique().tolist())
        status_options = sorted(bundle.work_packages["wp_status"].dropna().unique().tolist())
        priority_options = sorted(bundle.work_packages["wp_priority"].dropna().unique().tolist())

        project_filter = st.multiselect("Projetos", project_options)
        status_filter = st.multiselect("Status", status_options)
        priority_filter = st.multiselect("Prioridade", priority_options)

        st.divider()
        st.caption("Desenvolvido para análise executiva.")

    # --- FILTRAGEM ---
    filtered = _apply_filters(bundle, project_filter, status_filter, priority_filter)

    # --- RENDERIZAÇÃO ---
    # (ADICIONADO / CORRIGIDO) Header com logo à esquerda + título central
    _render_brand_header(logo_path=str(logo_path))

    _render_header()
    _render_kpis(filtered)

    st.markdown("---")

    _render_distribution_charts(filtered)

    st.markdown("---")

    _render_productivity_charts(filtered)

    st.markdown("---")

    # Tabela Detalhada com abas
    st.subheader("📋 Detalhamento das Atividades")
    tab1, tab2 = st.tabs(["Visão Geral", "Atrasados"])

    with tab1:
        # Formatação da tabela para ficar mais bonita
        display_df = filtered.work_packages[[
            "wp_id", "wp_subject", "project_name", "wp_status", "wp_priority", "assignee", "due_date", "done_ratio"
        ]].copy()

        st.dataframe(
            display_df,
            column_config={
                "done_ratio": st.column_config.ProgressColumn("Progresso", format="%d%%", min_value=0, max_value=100),
                "due_date": st.column_config.DateColumn("Prazo"),
                "wp_id": "ID",
                "wp_subject": "Assunto",
                "project_name": "Projeto",
                "wp_status": "Status",
                "wp_priority": "Prioridade",
                "assignee": "Responsável"
            },
            use_container_width=True,
            hide_index=True
        )

    with tab2:
        if "is_late" in filtered.work_packages.columns:
            late_df = filtered.work_packages[filtered.work_packages["is_late"] == True]
            if not late_df.empty:
                st.warning(f"Existem {len(late_df)} atividades com prazo vencido.")
                st.dataframe(late_df[["wp_id", "wp_subject", "project_name", "due_date", "assignee"]], use_container_width=True, hide_index=True)
            else:
                st.success("Nenhuma atividade atrasada nos filtros selecionados!")


if __name__ == "__main__":
    main()
