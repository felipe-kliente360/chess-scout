import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import time

from modules.fetcher import fetch_games
from modules.analyzer import analyze_games
from modules.stats import compute_stats
from modules.reporter import generate_diagnostic, generate_opponent_guide, save_reports

st.set_page_config(
    page_title="Chess Scout",
    page_icon="♟",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.metric-card {
    background: #1e1e2e;
    border-radius: 10px;
    padding: 1rem;
    text-align: center;
    border: 1px solid #313244;
}
.metric-value {
    font-size: 2rem;
    font-weight: bold;
    color: #cba6f7;
}
.metric-label {
    color: #a6adc8;
    font-size: 0.85rem;
}
</style>
""", unsafe_allow_html=True)

st.title("♟ Chess Scout")
st.caption("Analise jogadores do Chess.com e descubra como vencê-los")

with st.sidebar:
    st.header("Configuração")
    username_input = st.text_input("Username do Chess.com", placeholder="ex: magnuscarlsen")
    time_class_options = {"Todas": None, "Blitz": "blitz", "Rapid": "rapid", "Bullet": "bullet"}
    selected_tc = st.selectbox("Modalidade", list(time_class_options.keys()))
    time_class_filter = time_class_options[selected_tc]

    analyze_btn = st.button("Analisar Jogador", type="primary", use_container_width=True)

    if "diagnostic_md" in st.session_state:
        st.divider()
        st.download_button(
            "⬇ Baixar DIAGNOSTICO.md",
            data=st.session_state["diagnostic_md"],
            file_name=f"DIAGNOSTICO_{st.session_state['analyzed_username']}.md",
            mime="text/markdown",
            use_container_width=True,
        )
        st.download_button(
            "⬇ Baixar GUIA_ADVERSARIO.md",
            data=st.session_state["guide_md"],
            file_name=f"GUIA_ADVERSARIO_{st.session_state['analyzed_username']}.md",
            mime="text/markdown",
            use_container_width=True,
        )

if analyze_btn and username_input:
    username = username_input.strip().lower()

    progress_bar = st.progress(0)
    status_text = st.empty()

    status_text.text("Buscando partidas...")
    progress_bar.progress(5)

    try:
        def fetch_progress(found, target):
            pct = min(int(found / target * 25), 25)
            progress_bar.progress(5 + pct)
            status_text.text(f"Buscando partidas... ({found}/{target})")

        profile, games = fetch_games(
            username,
            target=100,
            time_class_filter=time_class_filter,
            progress_callback=fetch_progress,
        )
        progress_bar.progress(30)

        if not games:
            st.error("Nenhuma partida encontrada para esse jogador/modalidade.")
            st.stop()

        status_text.text("Analisando com Stockfish...")
        progress_bar.progress(35)

        try:
            def analysis_progress(done, total):
                pct = int(done / total * 40)
                progress_bar.progress(35 + pct)
                status_text.text(f"Analisando com Stockfish... ({done}/{total})")

            analyzed_games = analyze_games(games, username, progress_callback=analysis_progress)
        except FileNotFoundError:
            st.warning("Stockfish não encontrado — análise de movimentos desabilitada. Instale com `brew install stockfish` ou `apt install stockfish`.")
            analyzed_games = games

        progress_bar.progress(75)
        status_text.text("Calculando estatísticas...")
        stats = compute_stats(analyzed_games, username)

        progress_bar.progress(85)
        status_text.text("Gerando relatórios...")
        diagnostic_md = generate_diagnostic(stats, username)
        guide_md = generate_opponent_guide(stats, username)
        save_reports(username, diagnostic_md, guide_md)

        progress_bar.progress(100)
        status_text.text("Análise concluída!")
        time.sleep(0.5)

        st.session_state["stats"] = stats
        st.session_state["profile"] = profile
        st.session_state["diagnostic_md"] = diagnostic_md
        st.session_state["guide_md"] = guide_md
        st.session_state["analyzed_username"] = username

        progress_bar.empty()
        status_text.empty()

    except ValueError as e:
        st.error(str(e))
        st.stop()
    except Exception as e:
        st.error(f"Erro inesperado: {e}")
        st.stop()

if "stats" in st.session_state:
    stats = st.session_state["stats"]
    profile = st.session_state["profile"]
    analyzed_username = st.session_state["analyzed_username"]

    tab1, tab2, tab3, tab4 = st.tabs(["Visão Geral", "Análise de Erros", "Aberturas", "Relatórios Completos"])

    with tab1:
        col_avatar, col_info = st.columns([1, 3])

        with col_avatar:
            avatar_url = profile.get("avatar")
            if avatar_url:
                st.image(avatar_url, width=120)
            else:
                st.markdown("### ♟")
            st.markdown(f"**{profile.get('username', analyzed_username)}**")
            country = profile.get("country", "")
            if country:
                st.caption(country.split("/")[-1])

        with col_info:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Rating", stats.get("current_rating", "N/A"))
            m2.metric("Partidas", stats.get("total_games", 0))
            m3.metric("Taxa de Vitória", f"{stats.get('win_rate', 0):.1f}%")
            m4.metric("Oponentes (média)", stats.get("avg_opponent_rating", "N/A"))

        st.divider()

        col_pie, col_bar = st.columns(2)

        with col_pie:
            st.subheader("Resultados Gerais")
            wins = stats.get("wins", 0)
            losses = stats.get("losses", 0)
            draws = stats.get("draws", 0)
            fig_pie = px.pie(
                names=["Vitórias", "Derrotas", "Empates"],
                values=[wins, losses, draws],
                color_discrete_sequence=["#a6e3a1", "#f38ba8", "#89b4fa"],
                hole=0.4,
            )
            fig_pie.update_layout(margin=dict(t=10, b=10))
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_bar:
            st.subheader("Performance por Modalidade")
            tc_stats = stats.get("time_class_stats", {})
            if tc_stats:
                tc_df = pd.DataFrame([
                    {"Modalidade": k.capitalize(), "Vitórias": v["wins"], "Derrotas": v["losses"], "Empates": v["draws"]}
                    for k, v in tc_stats.items()
                ])
                fig_bar = px.bar(
                    tc_df,
                    x="Modalidade",
                    y=["Vitórias", "Derrotas", "Empates"],
                    color_discrete_sequence=["#a6e3a1", "#f38ba8", "#89b4fa"],
                    barmode="group",
                )
                fig_bar.update_layout(margin=dict(t=10, b=10))
                st.plotly_chart(fig_bar, use_container_width=True)

    with tab2:
        error_stats = stats.get("error_stats", {})
        averages = error_stats.get("averages_per_game", {})
        bp = error_stats.get("blunders_by_phase", {})

        if averages:
            col_e1, col_e2 = st.columns(2)

            with col_e1:
                st.subheader("Média de Movimentos por Partida")
                labels_pt = {
                    "excellent": "Excelente",
                    "good": "Boa",
                    "inaccuracy": "Imprecisão",
                    "mistake": "Erro",
                    "blunder": "Blunder",
                }
                colors = ["#a6e3a1", "#89b4fa", "#fab387", "#f38ba8", "#cba6f7"]
                avg_data = {labels_pt.get(k, k): v for k, v in averages.items()}
                fig_avg = go.Figure(go.Bar(
                    x=list(avg_data.keys()),
                    y=list(avg_data.values()),
                    marker_color=colors[:len(avg_data)],
                ))
                fig_avg.update_layout(margin=dict(t=10, b=10), xaxis_title="", yaxis_title="Média")
                st.plotly_chart(fig_avg, use_container_width=True)

            with col_e2:
                st.subheader("Blunders por Fase")
                if bp:
                    phase_labels = {"opening": "Abertura", "middlegame": "Meio de Jogo", "endgame": "Final"}
                    phase_data = {phase_labels.get(k, k): v for k, v in bp.items()}
                    fig_phase = go.Figure(go.Bar(
                        x=list(phase_data.keys()),
                        y=list(phase_data.values()),
                        marker_color=["#89b4fa", "#cba6f7", "#f38ba8"],
                    ))
                    fig_phase.update_layout(margin=dict(t=10, b=10))
                    st.plotly_chart(fig_phase, use_container_width=True)

            st.subheader("Top 5 Tipos de Erro")
            top_errors = error_stats.get("top_errors", [])
            if top_errors:
                err_df = pd.DataFrame(top_errors)
                st.dataframe(err_df, use_container_width=True, hide_index=True)
        else:
            st.info("Análise de erros não disponível (Stockfish não encontrado).")

    with tab3:
        openings_white = stats.get("openings_white", [])
        openings_black = stats.get("openings_black", [])

        col_w, col_b = st.columns(2)

        with col_w:
            st.subheader("Com Brancas")
            if openings_white:
                best_w = stats.get("best_opening_white")
                worst_w = stats.get("worst_opening_white")
                if best_w:
                    st.success(f"Melhor: {best_w['opening']} ({best_w['win_rate']:.1f}% em {best_w['games']} partidas)")
                if worst_w:
                    st.error(f"Pior: {worst_w['opening']} ({worst_w['win_rate']:.1f}% em {worst_w['games']} partidas)")
                df_w = pd.DataFrame(openings_white)[["opening", "games", "win_rate"]]
                df_w.columns = ["Abertura", "Partidas", "% Vitória"]
                st.dataframe(df_w, use_container_width=True, hide_index=True)

        with col_b:
            st.subheader("Com Pretas")
            if openings_black:
                best_b = stats.get("best_opening_black")
                worst_b = stats.get("worst_opening_black")
                if best_b:
                    st.success(f"Melhor: {best_b['opening']} ({best_b['win_rate']:.1f}% em {best_b['games']} partidas)")
                if worst_b:
                    st.error(f"Pior: {worst_b['opening']} ({worst_b['win_rate']:.1f}% em {worst_b['games']} partidas)")
                df_b = pd.DataFrame(openings_black)[["opening", "games", "win_rate"]]
                df_b.columns = ["Abertura", "Partidas", "% Vitória"]
                st.dataframe(df_b, use_container_width=True, hide_index=True)

    with tab4:
        col_diag, col_guide = st.columns(2)

        with col_diag:
            st.subheader("Diagnóstico")
            st.markdown(st.session_state["diagnostic_md"])

        with col_guide:
            st.subheader("Guia do Adversário")
            st.markdown(st.session_state["guide_md"])

else:
    st.info("Digite um username na barra lateral e clique em **Analisar Jogador** para começar.")
    st.markdown("""
### Como usar

1. Digite o username de qualquer jogador do Chess.com na barra lateral
2. Escolha a modalidade (ou deixe em "Todas")
3. Clique em **Analisar Jogador**
4. Explore os relatórios nas abas

### O que você vai obter

- **Diagnóstico completo** do jogador com pontos fortes, fracos e plano de estudo
- **Guia do adversário** com estratégias específicas para vencê-lo
- Análise de aberturas, erros por fase e perfil de jogo
    """)
