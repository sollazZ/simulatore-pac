import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURAZIONE PAGINA E TEMA ---
st.set_page_config(page_title="Simulatore PAC Avanzato", layout="centered")

# --- INPUT UTENTE ---
with st.sidebar:
    st.header("🎨 Aspetto")
    # Opzione per forzare il colore di sfondo
    tema = st.radio("Sfondo Applicazione", ["Predefinito", "Chiaro (Forzato)", "Scuro (Forzato)"])
    if tema == "Chiaro (Forzato)":
        st.markdown("<style>.stApp { background-color: #FFFFFF; color: #000000; }</style>", unsafe_allow_html=True)
    elif tema == "Scuro (Forzato)":
        st.markdown("<style>.stApp { background-color: #0E1117; color: #FFFFFF; }</style>", unsafe_allow_html=True)

    st.header("⚙️ Parametri Base")
    capitale_iniziale = st.number_input("Capitale di partenza (€)", min_value=0, value=0, step=1000)
    mensile = st.number_input("Importo PAC iniziale (€/mese)", min_value=10, value=100, step=10)
    anni = st.slider("Durata in anni", 1, 40, 10)
    rendimento_annuo = st.slider("Rendimento annuo stimato (%)", 0.0, 15.0, 7.0) / 100

    # Menu a tendina per le modifiche al PAC
    with st.expander("🔄 Modifiche PAC (Max 3)"):
        st.write("Cambia l'importo mensile da un certo anno in poi:")
        c1, c2 = st.columns(2)
        anno_m1 = c1.number_input("Da Anno (A)", min_value=0, max_value=anni, value=0)
        imp_m1 = c2.number_input("Nuovo Imp. A", min_value=0, value=0, step=10)
        
        anno_m2 = c1.number_input("Da Anno (B)", min_value=0, max_value=anni, value=0)
        imp_m2 = c2.number_input("Nuovo Imp. B", min_value=0, value=0, step=10)
        
        anno_m3 = c1.number_input("Da Anno (C)", min_value=0, max_value=anni, value=0)
        imp_m3 = c2.number_input("Nuovo Imp. C", min_value=0, value=0, step=10)

        pac_changes = {}
        if anno_m1 > 0: pac_changes[anno_m1] = imp_m1
        if anno_m2 > 0: pac_changes[anno_m2] = imp_m2
        if anno_m3 > 0: pac_changes[anno_m3] = imp_m3

    # Menu a tendina per versamenti extra
    with st.expander("💰 Versamenti Extra (Una Tantum)"):
        st.write("Aggiungi grosse somme all'inizio di anni specifici:")
        c3, c4 = st.columns(2)
        anno_ex1 = c3.number_input("Anno Extra 1", min_value=0, max_value=anni, value=0)
        imp_ex1 = c4.number_input("Importo 1 (€)", min_value=0, value=0, step=1000)
        
        anno_ex2 = c3.number_input("Anno Extra 2", min_value=0, max_value=anni, value=0)
        imp_ex2 = c4.number_input("Importo 2 (€)", min_value=0, value=0, step=1000)

        lump_sums = {}
        if anno_ex1 > 0: lump_sums[anno_ex1] = imp_ex1
        if anno_ex2 > 0: lump_sums[anno_ex2] = imp_ex2

    st.header("📈 Macro e Fiscali")
    inflazione_annua = st.slider("Inflazione annua attesa (%)", 0.0, 10.0, 2.0) / 100
    tassazione = st.slider("Tassazione plusvalenze (%)", 0.0, 30.0, 26.0) / 100

# --- CALCOLI ---
tasso_mensile = (1 + rendimento_annuo) ** (1/12) - 1

dati_annuali = []
capitale_versato = capitale_iniziale
valore_nominale = capitale_iniziale
pac_corrente = mensile

for anno in range(1, anni + 1):
    # Applica eventuali cambi di PAC per questo anno
    if anno in pac_changes:
        pac_corrente = pac_changes[anno]
    
    # Aggiungi eventuali versamenti extra (una tantum)
    if anno in lump_sums:
        capitale_versato += lump_sums[anno]
        valore_nominale += lump_sums[anno]
        
    for mese in range(12):
        capitale_versato += pac_corrente
        valore_nominale = (valore_nominale + pac_corrente) * (1 + tasso_mensile)
        
    # Calcolo Tasse e Valore Netto
    plusvalenza = valore_nominale - capitale_versato
    tasse = plusvalenza * tassazione if plusvalenza > 0 else 0
    valore_netto = valore_nominale - tasse
    
    # Calcolo Potere d'acquisto
    valore_reale_netto = valore_netto / ((1 + inflazione_annua) ** anno)
    
    # Tabella con nomi brevi per evitare scorrimento laterale
    dati_annuali.append({
        "Anno": anno,
        "Versato": round(capitale_versato, 2),
        "V. Netto": round(valore_netto, 2),
        "Potere Acq.": round(valore_reale_netto, 2)
    })

df = pd.DataFrame(dati_annuali)

# --- VISUALIZZAZIONE ---
st.title("📈 Simulatore PAC Avanzato")

st.subheader("Crescita del Capitale Netto")
# Grafico a linee con Plotly per gestire lo spessore
fig_line = px.line(
    df, x="Anno", y=["V. Netto", "Potere Acq.", "Versato"], 
    color_discrete_sequence=['#2ca02c', '#d62728', '#1f77b4']
)
# Linee spesse e marcate
fig_line.update_traces(line=dict(width=4)) 
st.plotly_chart(fig_line, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Composizione Finale")
    totale_versato = df["Versato"].iloc[-1]
    totale_interessi_netti = df["V. Netto"].iloc[-1] - totale_versato
    
    fig_pie = px.pie(
        values=[totale_versato, totale_interessi_netti], 
        names=['Capitale Versato', 'Interessi Netti'],
        color_discrete_sequence=['#1f77b4', '#2ca02c']
    )
    # Contorno nero marcato per i bordi della torta
    fig_pie.update_traces(marker=dict(line=dict(color='#000000', width=2)))
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    st.metric("Valore Netto Finale", f"€{df['V. Netto'].iloc[-1]:,.2f}")
    
    perdita_inflazione = df['V. Netto'].iloc[-1] - df['Potere Acq.'].iloc[-1]
    st.metric(
        "Potere d'Acq. Reale Netto", 
        f"€{df['Potere Acq.'].iloc[-1]:,.2f}", 
        delta=f"Perdita per inflazione: -€{perdita_inflazione:,.2f}", 
        delta_color="inverse"
    )
    
    tasse_totali = plusvalenza * tassazione if plusvalenza > 0 else 0
    st.caption(f"Tasse stimate pagate allo Stato: **€{tasse_totali:,.2f}**")

# --- TABELLA E DOWNLOAD ---
st.subheader("Andamento Anno per Anno")
st.table(df)

csv = df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Scarica i dati in CSV",
    data=csv,
    file_name='simulazione_pac_avanzata.csv',
    mime='text/csv',
)
