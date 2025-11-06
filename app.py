import streamlit as st
import pandas as pd
import numpy as np
import random
from datetime import datetime
from PIL import Image
from pymongo import MongoClient

# ---------------------- Configuración de página ----------------------
st.set_page_config(page_title="Recomendador Café Quiteñito", page_icon="☕", layout="wide")
st.title("☕ Recomendador de Platos - Arquitectura Lambda (Café Quiteñito)")

# ---------------------- Conexión a MongoDB Atlas ----------------------
# Cambia el siguiente URI por el de tu cuenta de Atlas
MONGO_URI = "mongodb+srv://karinachisaguanoest_db_user:<yhJcJgKtQV8zbAvo>@cluster0.9ks8qge.mongodb.net/?appName=Cluster0"

try:
    client = MongoClient(MONGO_URI)
    db = client["cafeteria_db"]
    coleccion_historico = db["valoraciones_historicas"]
    coleccion_recomendaciones = db["recomendaciones"]
    st.sidebar.success("✅ Conectado a MongoDB Atlas correctamente")
except Exception as e:
    st.sidebar.error(f"❌ Error al conectar a MongoDB: {e}")

# ---------------------- Estilos personalizados ----------------------
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
# CAPA BATCH - Datos históricos (CSV → MongoDB)
# -----------------------------------------------------------
st.header("🧩 Capa Batch - Datos históricos")

platos = ["Capuccino", "Latte", "Mocaccino", "Cheesecake", "Croissant", "Sandwich de Jamón"]

# Cargar CSV
historico = pd.read_csv("historico_cafeteria_2025.csv")
historico["valoracion"] = pd.to_numeric(historico["valoracion"], errors="coerce")

# Mostrar
st.dataframe(historico.head(), use_container_width=True)
st.info("Estos datos representan las valoraciones históricas de los clientes del Café Aroma.")

# Guardar en MongoDB si aún no existe información
if coleccion_historico.count_documents({}) == 0:
    datos_dict = historico.to_dict("records")
    coleccion_historico.insert_many(datos_dict)
    st.success("📦 Datos del CSV cargados y guardados en MongoDB Atlas.")
else:
    st.warning("⚠️ Los datos históricos ya existen en MongoDB. No se volverán a insertar.")

# -----------------------------------------------------------
# CAPA DE VELOCIDAD - Nuevas valoraciones en tiempo real
# -----------------------------------------------------------
st.header("⚡ Capa de Velocidad - Nuevas valoraciones en tiempo real")

nuevo_usuario = st.text_input("👤 Nombre del cliente", "Cliente_nuevo")
plato_nuevo = st.selectbox("🍽️ Selecciona el plato", platos)
valor_nuevo = st.slider("⭐ Valoración del plato (1-5)", 1, 5, 4)

if st.button("Registrar valoración"):
    nueva_valoracion = {
        "usuario": nuevo_usuario,
        "plato": plato_nuevo,
        "valoracion": valor_nuevo,
        "fecha": datetime.now()
    }
    
    # Guardar en MongoDB
    coleccion_historico.insert_one(nueva_valoracion)
    st.success("✅ Nueva valoración registrada y guardada en MongoDB.")

# -----------------------------------------------------------
# CAPA DE SERVICIO - Generación de recomendaciones
# -----------------------------------------------------------
st.header("💡 Capa de Servicio - Recomendaciones actualizadas")

# Obtener todos los datos de MongoDB
datos_totales = pd.DataFrame(list(coleccion_historico.find({}, {"_id": 0})))

if not datos_totales.empty:
    # Calcular promedio de valoraciones por plato
    recomendaciones = datos_totales.groupby("plato")["valoracion"].mean().reset_index()
    recomendaciones = recomendaciones.sort_values(by="valoracion", ascending=False)

    # Guardar recomendaciones actuales en MongoDB
    coleccion_recomendaciones.delete_many({})  # Limpia las anteriores
    coleccion_recomendaciones.insert_many(recomendaciones.to_dict("records"))

    # Mostrar tabla
    st.subheader("🍰 Platos recomendados (histórico + tiempo real)")
    st.table(recomendaciones.style.format({"valoracion": "{:.2f}"}))

    # Plato más recomendado
    top_plato = recomendaciones.iloc[0]["plato"]
    st.success(f"🥇 Recomendación destacada del momento: **{top_plato}**")

    # Visualización
    st.subheader("📈 Valoraciones promedio por plato")
    st.bar_chart(recomendaciones.set_index("plato"))
else:
    st.warning("No se encontraron datos en MongoDB para generar recomendaciones.")
