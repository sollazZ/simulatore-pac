# --- COPIA E INCOLLA QUESTA SEZIONE IN APP.PY ---

with col1:
    st.subheader("Composizione Finale")
    totale_versato = df["Versato"].iloc[-1]
    totale_interessi_netti = df["V. Netto"].iloc[-1] - totale_versato
    
    # GRAFICO A TORTA CON CONTORNI NERI
    fig_pie = px.pie(
        values=[totale_versato, totale_interessi_netti], 
        names=['<b>Capitale Versato</b>', '<b>Interessi Netti</b>'],
        # Sequenza colori: [Versato (Blu iOS), Interessi (Giallo iOS)]
        color_discrete_sequence=['#007aff', '#ffcc00']
    )

    # --- NUOVA LOGICA: Contorni NERI in modalità Scuro ---
    # Prima usavamo "#ffffff" (bianco) in scuro. Ora lo forziamo a nero.
    # Questo parametro controlla SIA le fette che i quadratini della legenda.
    pie_border_color = "black" if tema == "Scuro" else plot_text_color
    
    # Applichiamo la modifica ai bordi (marker line)
    fig_pie.update_traces(marker=dict(line=dict(color=pie_border_color, width=2)))
    
    # Gestione dinamica tema grafico a torta (sfondi e testo)
    fig_pie.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color=plot_text_color,
        # La legenda eredita il contorno nero che abbiamo impostato sopra
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=plot_text_color))
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# --- FINE SEZIONE DA COPIARE ---
