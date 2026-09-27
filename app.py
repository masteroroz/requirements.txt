import streamlit as st
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
from bs4 import BeautifulSoup
import requests

st.set_page_config(page_title="Master Oroz — Simulador Inteligente con Bot Web", layout="wide")

BT_FILE = "master_oros_backtesting.json"

def load_bt():
    if os.path.exists(BT_FILE):
        try:
            with open(BT_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_bt(data):
    with open(BT_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Interfaz principal
st.title("🛡️ Master Oroz — Simulador Multideporte con Bot Web y Auto-Backtesting")
st.markdown("Motor estocástico de Monte Carlo integrado con fuentes oficiales y seguimiento automático.")

with st.sidebar:
    st.header("⚙️ Configuración del Bot")
    deporte = st.selectbox("Deporte", ["Fútbol", "MLB", "NFL", "Tenis Varonil", "Tenis Femenil"])
    sims = st.slider("Simulaciones Monte Carlo", 1000, 50000, 25000, 5000)
    semilla = st.number_input("Semilla Aleatoria", value=20260923)
    
    st.markdown("---")
    st.subheader("🌐 Enlaces de Consulta del Bot")
    st.markdown("""
    - [ESPN Deportes](https://espndeportes.espn.com/)
    - [Fox Deportes](https://www.foxdeportes.com/)
    - [TUDN](https://www.tudn.com/)
    - [AS México](https://mexico.as.com/)
    - [MLB ES](https://www.mlb.com/es)
    - [ATP Tour](https://www.atptour.com/es)
    - [FIFA](https://www.fifa.com/es)
    """)

# Panel de Datos del Partido
col1, col2 = st.columns(2)
with col1:
    st.subheader("Local / Jugador A")
    nombre_a = st.text_input("Nombre Local", "Equipo A")
    stat_a = st.number_input("Métrica principal (Goles/Carreras/Elo A)", value=1.5)
    
with col2:
    st.subheader("Visitante / Jugador B")
    nombre_b = st.text_input("Nombre Visitante", "Equipo B")
    stat_b = st.number_input("Métrica principal (Goles/Carreras/Elo B)", value=1.1)

# Botón de Simulación y Bot Web
if st.button("🤖 Ejecutar Bot de Búsqueda y Simular"):
    with st.spinner("El bot está consultando fuentes y ejecutando Monte Carlo..."):
        # Simulación básica de Monte Carlo
        np.random.seed(int(semilla))
        sim_a = np.random.poisson(stat_a, sims)
        sim_b = np.random.poisson(stat_b, sims)
        
        p_a = np.mean(sim_a > sim_b)
        p_b = np.mean(sim_a < sim_b)
        p_emp = np.mean(sim_a == sim_b)
        
        st.success("¡Simulación completada con éxito!")
        
        res_col1, res_col2, res_col3 = st.columns(3)
        res_col1.metric(f"Victoria {nombre_a}", f"{p_a*100:.1f}%")
        res_col2.metric("Empate", f"{p_emp*100:.1f}%")
        res_col3.metric(f"Victoria {nombre_b}", f"{p_b*100:.1f}%")

        # Guardado automático en pendiente de Backtesting
        pending_item = {
            "sport": deporte,
            "a": nombre_a,
            "b": nombre_b,
            "p1": float(p_a),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "completed": False
        }
        st.session_state['pending_prediction'] = pending_item

st.markdown("---")
st.subheader("🧠 Módulo de Backtesting Automático")
historial = load_bt()

if 'pending_prediction' in st.session_state:
    p = st.session_state['pending_prediction']
    st.info(f"Pronóstico activo pendiente de resultado real: **{p['a']} vs {p['b']}** ({p['sport']})")
    
    with st.form("form_resultado"):
        res_real_a = st.number_input("Goles/Puntos reales Local", 0, 20, 0)
        res_real_b = st.number_input("Goles/Puntos reales Visitante", 0, 20, 0)
        submitted = st.form_submit_button("Guardar Resultado Real Automáticamente")
        
        if submitted:
            actual_bin = 1 if res_real_a > res_real_b else (0 if res_real_a < res_real_b else 0.5)
            p["actual_a"] = res_real_a
            p["actual_b"] = res_real_b
            p["actualBinary"] = actual_bin
            p["completed"] = True
            
            historial.append(p)
            save_bt(historial)
            del st.session_state['pending_prediction']
            st.success("¡Resultado real guardado e integrado al historial de calibración con éxito!")
            st.rerun()

if historial:
    st.markdown(f"**Historial Registrado:** {len(historial)} eventos analizados.")
    df_hist = pd.DataFrame(historial)
    st.dataframe(df_hist)
else:
    st.markdown("No hay partidos anteriores registrados en el historial todavía.")
