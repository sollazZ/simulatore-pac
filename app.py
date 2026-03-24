import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURAZIONE PAGINA E TEMA ---
st.set_page_config(page_title="Simulatore PAC Apple Style", layout="centered")

# --- INPUT UTENTE CON EFFETTO LIQUID GLASS E COLORI CORRETTI ---
with st.sidebar:
    st.header("🎨 Stile (Liquid Glass)")
    tema = st.radio("Tema Visivo", ["Scuro", "Chiaro"])
    
    if tema == "Scuro":
        plot_text_color = "#f5f5f7"
        plot_grid_color = "rgba(255, 255, 255, 0.1)"
        css_theme_logic = """
        .stApp { background-color: #000000; color: #f5f5f7; }
        [data-testid="stSidebar"] { background-color: rgba(20, 20, 20, 0.6) !important; backdrop-filter: blur(12px); border-right: 1px solid rgba(255,255,255,0.1); }
        [data-testid="metric-container"] { background-color: rgba(255, 255, 255, 0.05); border-radius: 15px; padding: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); border: 1px solid rgba(255, 255, 255, 0.1); }
        /* Forza il colore e i grassetti per il tema scuro */
        h1, h2, h3, h4, h5, h6, p, span, label, th, td { color: #f5f5f7 !important; }
        div[data-testid="stMetricValue"] { color: #f5f5f7 !important; font-weight: 900 !important; }
        /* Stile pulsante download */
        .stDownloadButton button { border-color: rgba(255,255,255,0.4) !important; background-color: transparent !important; }
        .stDownloadButton button p { color: #f5f5f7 !important; font-weight: bold !important; }
        """
    else:
        plot_text_color = "#1d1d1f"
        plot_grid_color = "#dcdcdc"
        css_theme_logic = """
        /* Sfondo BIANCO SOLIDO per il tema chiaro */
        .stApp { background-color: #FFFFFF; color: #1d1d1f; }
        [data-testid="stSidebar"] { background-color: rgba(255, 255, 255, 0.4) !important; backdrop-filter: blur(12px); }
        [data-testid="metric-container"] { background-color: rgba(255, 255, 255, 0.6); border-radius: 15px; padding: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid rgba(255, 255, 255, 0.5); }
        /* Forza il colore e i grassetti per il tema chiaro */
        h1, h2, h3, h4, h5, h6, p, span, label, th, td { color: #1d1d1f !important; }
        div[data-testid="stMetricValue"] { color: #1d1d1f !important; font-weight: 900 !important; }
        /* Stile pulsante download */
        .stDownloadButton button { border-color: rgba(29,29,31,0.4) !important; background-color: transparent !important; }
        .stDownloadButton button p { color: #1d1d1f !important; font-weight: bold !important; }
        """

    st.markdown(f"<style>{css_theme_logic}</style>", unsafe_allow_html=True)

    st.header("⚙️ Parametri Base")
    nome_piano = st.text_input("Nome del Piano di Accumulo", value="Il mio PAC")
    
    capitale_iniziale = st.number_input("Capitale di partenza (€)", min_value=0, value=0, step=1000)
    mensile = st.number_input("Importo PAC iniziale (€/mese)", min_value=10, value=100, step=10)
    anni = st.number_input("Durata (Anni)", min_value=1, max_value=50, value=10, step=1)
    rendimento_annuo = st.number_input("Rendimento annuo stimato (%)", min_value=0.0, max_value=20.0, value=7.0, step=0.1) / 100

    with st.expander("🔄 Modifiche PAC (Max 3)"):
        c1, c2 = st.columns(2)
        anno_m1 = c1.number_input("Da Anno (A)", min_value=0, max_value=int(anni), value=0)
        imp_m1 = c2.number_input("Nuovo Imp. A", min_value=0, value=0, step=10)
        anno_m2 = c1.number_input("Da Anno (B)", min_value=0, max_value=int(anni), value=0)
        imp_m2 = c2.number_input("Nuovo Imp. B", min_value=0, value=0, step=10)
        anno_m3 = c1.number_input("Da Anno (C)", min_value=0, max_value=int(anni), value=0)
        imp_m3 = c2.number_input("Nuovo Imp. C", min_value=0, value=0, step=10)

        pac_changes = {}
        if anno_m1 > 0: pac_changes[anno_m1] = imp_m1
        if anno_m2 > 0: pac_changes[anno_m2] = imp_m2
        if anno_m3 > 0: pac_changes[anno_m3] = imp_m3

    with st.expander("💰 Versamenti Extra"):
        c3, c4 = st.columns(2)
        anno_ex1 = c3.number_input("Anno Extra 1", min_value=0, max_value=int(anni), value=0)
        imp_ex1 = c4.number_input("Importo 1 (€)", min_value=0, value=0, step=1000)
        anno_ex2 = c3.number_input("Anno Extra 2", min_value=0, max_value=int(anni), value=0)
        imp_ex2 = c4.number_input("Importo 2 (€)", min_value=0, value=0, step=1000)

        lump_sums = {}
        if anno_ex1 > 0: lump_sums[anno_ex1] = imp_ex1
        if anno_ex2 > 0: lump_sums[anno_ex2] = imp_ex2

    st.header("📈 Macro e Fiscali")
    inflazione_annua = st.number_input("Inflazione annua attesa (%)", min_value=0.0, max_value=15.0, value=2.0, step=0.1) / 100
    tassazione = st.number_input("Tassazione plusvalenze (%)", min_value=0.0, max_value=50.0, value=26.0, step=0.1) / 100

# --- CALCOLI ---
tasso_mensile = (1 + rendimento_annuo) ** (1/12) - 1
dati_annuali = []
capitale_versato = capitale_iniziale
valore_nominale = capitale_iniziale
pac_corrente = mensile

for anno in range(1, int(anni) + 1):
    if anno in pac_changes:
        pac_corrente = pac_changes[anno]
    if anno in lump_sums:
        capitale_versato += lump_sums[anno]
        valore_nominale += lump_sums[anno]
        
    for mese in range(12):
        capitale_versato += pac_corrente
        valore_nominale = (valore_nominale + pac_corrente) * (1 + tasso_mensile)
        
    plusvalenza = valore_nominale - capitale_versato
    tasse = plusvalenza * tassazione if plusvalenza > 0 else 0
    valore_netto = valore_nominale - tasse
    valore_reale_netto = valore_netto / ((1 + inflazione_annua) ** anno)
    
    dati_annuali.append({
        "Anno": anno,
        "Versato": valore_netto - plusvalenza + tasse,
        "V. Netto": valore_netto,
        "Potere Acq.": valore_reale_netto
    })

df = pd.DataFrame(dati_annuali)

# --- VISUALIZZAZIONE ---
st.title(f"📈 {nome_piano}")

st.subheader("Crescita del Capitale Netto")
fig_line = px.line(
    df, x="Anno", y=["V. Netto", "Potere Acq.", "Versato"], 
    color_discrete_sequence=['#34c759', '#ff3b30', '#007aff'], # Verde, Rosso, Blu Apple
    labels={"value": "<b>Euro (€)</b>", "variable": "<b>Legenda</b>"}
)
fig_line.update_traces(line=dict(width=4)) 
fig_line.for_each_trace(lambda t: t.update(name=f"<b>{t.name}</b>"))

fig_line.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color=plot_text_color,
    hovermode="x unified",
    xaxis=dict(showgrid=True, gridcolor=plot_grid_color, tickfont=dict(color=plot_text_color), title_font=dict(color=plot_text_color), zeroline=True, zerolinecolor=plot_grid_color, zerolinewidth=2),
    yaxis=dict(showgrid=True, gridcolor=plot_grid_color, tickfont=dict(color=plot_text_color), title_font=dict(color=plot_text_color), zeroline=True, zerolinecolor=plot_grid_color, zerolinewidth=2),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=plot_text_color))
)
st.plotly_chart(fig_line, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Composizione Finale")
    totale_versato = df["Versato"].iloc[-1]
    totale_interessi_netti = df["V. Netto"].iloc[-1] - totale_versato
    
    # GRAFICO A TORTA CON I NUOVI COLORI: BLU E GIALLO
    fig_pie = px.pie(
        values=[totale_versato, totale_interessi_netti], 
        names=['<b>Capitale Versato</b>', '<b>Interessi Netti</b>'],
        # Sequenza colori: [Versato (Blu iOS), Interessi (Giallo iOS)]
        color_discrete_sequence=['#007aff', '#ffcc00']
    )
    pie_border_color = "#ffffff" if tema == "Scuro" else plot_text_color
    fig_pie.update_traces(marker=dict(line=dict(color=pie_border_color, width=2)))
    
    fig_pie.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color=plot_text_color,
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=plot_text_color))
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    st.metric("Valore Netto Finale", f"€ {int(df['V. Netto'].iloc[-1]):,}".replace(",", "."))
    
    perdita_inflazione = df['V. Netto'].iloc[-1] - df['Potere Acq.'].iloc[-1]
    st.metric(
        "Potere d'Acq. Reale Netto", 
        f"€ {int(df['Potere Acq.'].iloc[-1]):,}".replace(",", "."), 
        delta=f"Perdita per inflazione: -€ {int(perdita_inflazione):,}".replace(",", "."), 
        delta_color="inverse"
    )
    
    tasse_totali = plusvalenza * tassazione if plusvalenza > 0 else 0
    st.caption(f"Tasse stimate pagate allo Stato: **€ {int(tasse_totali):,}**".replace(",", "."))

# --- TABELLA FORMATTATA E DOWNLOAD ---
st.subheader("Andamento Anno per Anno")

df_display = df.copy()
df_display.set_index("Anno", inplace=True)

for col in ["Versato", "V. Netto", "Potere Acq."]:
    df_display[col] = df_display[col].apply(lambda x: f"€ {int(x):,}").str.replace(",", ".")

st.table(df_display)

csv = df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Scarica i dati in CSV",
    data=csv,
    file_name='simulazione_pac_personalizzata.csv',
    mime='text/csv',
)
