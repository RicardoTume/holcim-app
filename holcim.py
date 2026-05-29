import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date

# --- Configuración de credenciales ---
# Descarga tu archivo JSON de credenciales de Google Cloud y guárdalo en tu proyecto
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credenciales.json", scope)
client = gspread.authorize(creds)

# Abrir tu Google Sheet
sheet = client.open("Avance_Proyecto_Villa1").sheet1

st.title("App Proyecto Holcim - Registro y Dashboard")

# --- Formulario de registro ---
st.header("Registro Diario de Avances")

tarea = st.text_input("Tarea")
responsable = st.text_input("Responsable")
fecha_inicio = st.date_input("Fecha Inicio")
fecha_fin = st.date_input("Fecha Fin")
avance = st.slider("% Avance", 0, 100, 0)
observaciones = st.text_area("Observaciones")
estado = st.selectbox("Estado", ["Pendiente", "En curso", "Terminado"])

if st.button("Guardar avance"):
    sheet.append_row([tarea, responsable, str(fecha_inicio), str(fecha_fin),
                      avance, observaciones, estado])
    st.success("✅ Avance registrado correctamente en Google Sheets")

# --- Dashboard con agujas ---
st.header("Dashboard de Avance")

# Leer datos actualizados desde el Sheet
data = sheet.get_all_records()
df = pd.DataFrame(data)

def gauge_chart(valor, titulo):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=valor,
        title={'text': titulo},
        gauge={'axis': {'range': [0, 100]},
               'bar': {'color': "green"},
               'steps': [
                   {'range': [0, 40], 'color': "red"},
                   {'range': [40, 70], 'color': "yellow"},
                   {'range': [70, 100], 'color': "green"}]}))
    st.plotly_chart(fig)

# Mostrar gauges por área (ejemplo: primeras 3 filas)
if not df.empty:
    gauge_chart(df.loc[0, "%_Avance"], df.loc[0, "Tarea"])
    gauge_chart(df.loc[1, "%_Avance"], df.loc[1, "Tarea"])
    gauge_chart(df.loc[2, "%_Avance"], df.loc[2, "Tarea"])

st.subheader("Observaciones / Riesgos")
for obs in df["Observaciones"].dropna():
    st.write(f"- {obs}")
