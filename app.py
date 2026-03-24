import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Simulatore PAC", layout="centered")

st.title("📈 Simulatore PAC Reale (Inflazione e Tasse)")

# --- INPUT UTENTE ---
with st.sidebar:
    st.header("Parametri del Piano")
    mensile = st.number_input("Importo mensile (€)", min_value=10, value=100, step=10)
    anni = st.slider("Durata in anni", 1, 40, 10)
    rendimento_annuo = st.slider("Rendimento annuo stimato (%)", 0.0, 15.0, 7.0) / 100
    
    st.divider()
    st.header("Parametri Macro e Fiscali")
    inflazione_annua = st.slider("Inflazione annua attesa (%)", 0.0, 10.0, 2.0) / 100
    tassazione = st.slider("Tassazione plusvalenze (%)", 0.0, 30.0, 26.0) / 100

# --- CALCOLI ---
tasso_mensile = (1 + rendimento_annuo) ** (1/12) - 1

dati_annuali = []
capitale_versato = 0
valore_nominale = 0

for anno in range(1, anni + 1):
    for mese in range(12):
        capitale_versato += mensile
        valore_nominale = (valore_nominale + mensile) * (1 + tasso_mensile)
    
    # Calcolo Tasse e Valore Netto
    plusvalenza = valore_nominale - capitale_versato
    tasse = plusvalenza * tassazione if plusvalenza > 0 else 0
    valore_netto = valore_nominale - tasse
    
    # Calcolo Potere d'acquisto 
    valore_reale_netto = valore_netto / ((1 + inflazione_annua) ** anno)
    
    # Inserimento dati ottimizzato per evitare scorrimento orizzontale
    dati_annuali.append({
        "Anno": anno,
        "Versato": round(capitale_versato, 2),
        "Netto Nominale": round(valore_netto, 2),
        "Potere Acq. Netto": round(valore_reale_netto, 2)
    })

df = pd.DataFrame(dati_annuali)

# --- VISUALIZZAZIONE ---
st.subheader("Crescita del Capitale Netto")
st.line_chart(df.set_index("Anno")[["Netto Nominale", "Potere Acq. Netto", "Versato"]])

col1, col2 = st.columns(2)

with col1:
    st.subheader("Composizione Netta Finale")
    totale_versato = df["Versato"].iloc[-1]
    totale_interessi_netti = df["Netto Nominale"].iloc[-1] - totale_versato
    
    fig_pie = px.pie(
        values=[totale_versato, totale_interessi_netti], 
        names=['Capitale Versato', 'Interessi Netti'],
        color_discrete_sequence=['#1f77b4', '#2ca02c']
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    st.metric("Valore Netto Finale", f"€{df['Netto Nominale'].iloc[-1]:,.2f}")
    
    perdita_inflazione = df['Netto Nominale'].iloc[-1] - df['Potere Acq. Netto'].iloc[-1]
    st.metric(
        "Potere d'Acq. Reale Netto", 
        f"€{df['Potere Acq. Netto'].iloc[-1]:,.2f}", 
        delta=f"Perdita per inflazione: -€{perdita_inflazione:,.2f}", 
        delta_color="inverse"
    )
    
    tasse_totali = plusvalenza * tassazione if plusvalenza > 0 else 0
    st.caption(f"Tasse stimate pagate allo Stato: **€{tasse_totali:,.2f}**")

# --- TABELLA E DOWNLOAD ---
st.subheader("Andamento Anno per Anno")

# Tabella contabile compatta
st.table(df)

# Creazione del file CSV e pulsante di download
csv = df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Scarica i dati in CSV (Excel)",
    data=csv,
    file_name='simulazione_pac.csv',
    mime='text/csv',
)