import streamlit as st
import pandas as pd
import numpy as np
import random
from datetime import datetime
from PIL import Image

# ---------------------- Configuración de página ----------------------

st.set_page_config(page_title="Recomendador Café Quiteñito", page_icon="☕", layout="wide")
st.title("☕ Recomendador de Platos - Arquitectura Lambda (Café Quiteñito)")

# ---------------------- Inyectar estilos personalizados ----------------------
with open("style/main.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ---------------------- Mostrar logo y título ----------------------
logo = Image.open("Imagenes/logotecazuay.PNG")
col1, col2 = st.columns([3, 1])
with col1:
    st.title("📊  Café Quiteñito")
    st.markdown("#### Realizado por Karina Chisaguano")
with col2:
    st.image(logo, width=250)

# -----------------------------------------------------------
# TÍTULO Y DESCRIPCIÓN
# -----------------------------------------------------------




# -----------------------------------------------------------
# CAPA BATCH - Datos históricos simulados
# -----------------------------------------------------------
st.header("🧩 Capa Batch - Datos históricos")

platos = ["Capuccino", "Latte", "Mocaccino", "Cheesecake", "Croissant", "Sandwich de Jamón"]
usuarios = [f"Cliente_{i}" for i in range(1, 11)]

historico = pd.read_csv("historico_cafeteria_2025.csv")

historico["valoracion"] = pd.to_numeric(historico["valoracion"], errors="coerce")

st.dataframe(historico.head(), use_container_width=True)
st.info("Estos datos representan las valoraciones históricas de los clientes del Café Aroma.")

# -----------------------------------------------------------
# CAPA DE VELOCIDAD - Nuevas valoraciones en tiempo real
# -----------------------------------------------------------
st.header("⚡ Capa de Velocidad - Nuevas valoraciones en tiempo real")

nuevo_usuario = st.text_input("👤 Nombre del cliente", "Cliente_nuevo")
plato_nuevo = st.selectbox("🍽️ Selecciona el plato", platos)
valor_nuevo = st.slider("⭐ Valoración del plato (1-5)", 1, 5, 4)

if st.button("Registrar valoración"):
    nueva_valoracion = pd.DataFrame({
        "usuario": [nuevo_usuario],
        "plato": [plato_nuevo],
        "valoracion": [valor_nuevo],
        "fecha": [datetime.now()]
    })
    
    # Guardar nuevas valoraciones en la sesión
    if "valoraciones_nuevas" not in st.session_state:
        st.session_state["valoraciones_nuevas"] = pd.DataFrame(columns=["usuario", "plato", "valoracion", "fecha"])
    
    st.session_state["valoraciones_nuevas"] = pd.concat(
        [st.session_state["valoraciones_nuevas"], nueva_valoracion], ignore_index=True
    )
    st.success("✅ Nueva valoración registrada en tiempo real.")

# Mostrar valoraciones nuevas
if "valoraciones_nuevas" in st.session_state and not st.session_state["valoraciones_nuevas"].empty:
    st.subheader("📡 Flujo en vivo de nuevas valoraciones")
    st.dataframe(st.session_state["valoraciones_nuevas"], use_container_width=True)
else:
    st.warning("Aún no hay valoraciones recientes registradas.")

# -----------------------------------------------------------
# CAPA DE SERVICIO - Generación de recomendaciones
# -----------------------------------------------------------
st.header("💡 Capa de Servicio - Recomendaciones actualizadas")

# Combinar datos históricos con nuevas valoraciones
if "valoraciones_nuevas" in st.session_state and not st.session_state["valoraciones_nuevas"].empty:
    total = pd.concat([historico, st.session_state["valoraciones_nuevas"]])
else:
    total = historico

# Calcular promedio de valoraciones por plato
recomendaciones = total.groupby("plato")["valoracion"].mean().reset_index()
recomendaciones = recomendaciones.sort_values(by="valoracion", ascending=False)

# Mostrar tabla de recomendaciones
st.subheader("🍰 Platos recomendados (histórico + tiempo real)")
st.table(recomendaciones.style.format({"valoracion": "{:.2f}"}))

# Plato más recomendado
top_plato = recomendaciones.iloc[0]["plato"]
st.success(f"🥇 Recomendación destacada del momento: **{top_plato}**")

# Visualización gráfica
st.subheader("📈 Valoraciones promedio por plato")
st.bar_chart(recomendaciones.set_index("plato"))
