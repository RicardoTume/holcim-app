import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import gspread
from google.oauth2.service_account import Credentials
#from oauth2client.service_account import ServiceAccountCredentials
from datetime import date

def conectar_google_sheet():
    #data= sheet.get_all_records()
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    info = dict(st.secrets["gcp_service_account"])
    #st.write("Cuenta de servicio usada:", info["client_email"])
    #info["private_key"] = info["private_key"].replace("\\n", "\n")
    #st.write(info)  # Para verificar que todas las claves están presentes
    creds = Credentials.from_service_account_info(
        info,
        scopes=scope
    )

    client = gspread.authorize(creds)
    sheet = client.open_by_key("1hdQbE3Emhpn8YSbN2KM-yYwTgOXvC2fRkPXkxut5N3U").sheet1

    return sheet
    
#sheet = conectar_google_sheet()
data = sheet.get_all_records()
df = pd.DataFrame(data)

# Uso correcto de la función
#sheet = conectar_google_sheet()   # 👈 aquí llamas a la función
#data = sheet.get_all_records()    # ahora sí existe sheet
#st.write(data)                    # muestra los registros en tu app
#creds = ServiceAccountCredentials.from_json_keyfile_name("credenciales.json", scope)
#client = gspread.authorize(creds)

# Abrir tu Google Sheet
#sheet = client.open_by_key("1hdQbE3Emhpn8YSbN2KM-yYwTgOXvC2fRkPXkxut5N3U").sheet1

#st.title("App Proyecto Holcim - Registro y Dashboard")

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
