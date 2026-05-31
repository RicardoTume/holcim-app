import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import gspread
import traceback
from google.oauth2.service_account import Credentials
#from oauth2client.service_account import ServiceAccountCredentials
from datetime import date

# ----------- Modificado temporalmente ------
def conectar_google_sheet():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    info = dict(st.secrets["gcp_service_account"])
    
    #st.write("Email:", info.get("client_email"))
    #st.write("Project:", info.get("project_id"))
    #st.write("Tiene private key:", "private_key" in info)
    
    info["private_key"] = info["private_key"].replace("\\n", "\n")
    creds = Credentials.from_service_account_info(
        info,
        scopes=scope
    )

    client = gspread.authorize(creds)
    
    try:
        spreadsheet = client.open_by_key(
        "1hdQbE3Emhpn8YSbN2KM-yYwTgOXvC2fRkPXkxut5N3U"
        )
        #sheet = client.open_by_key(
            #"1hdQbE3Emhpn8YSbN2KM-yYwTgOXvC2fRkPXkxut5N3U"
        #).sheet1
    except Exception:
        st.code(traceback.format_exc())
        raise

    return spreadsheet
    #return sheet
    #sheet = client.open_by_key("1hdQbE3Emhpn8YSbN2KM-yYwTgOXvC2fRkPXkxut5N3U").sheet1

    #return sheet
# -------- fin de la modificacio -------    

#sheet = conectar_google_sheet()
#data = sheet.get_all_records()
#df = pd.DataFrame(data)

spreadsheet = conectar_google_sheet()

hoja_avances = spreadsheet.worksheet("Avances")
hoja_gantt = spreadsheet.worksheet("Gantt")

df_avances = pd.DataFrame(
    hoja_avances.get_all_records()
)

df_gantt = pd.DataFrame(
    hoja_gantt.get_all_records()
)

# Añadido por avances con chatgpt
st.subheader("🚨 Actividades sin Avance Registrado")

actividades_gantt = set(
    (
        df_gantt["EDT"].astype(str)
        + " - "
        + df_gantt["Nombre"].astype(str)
    )
)

actividades_avances = set(
    df_avances["Tarea"].astype(str)
)

sin_avance = sorted(
    actividades_gantt - actividades_avances
)

st.write(
    f"Actividades sin seguimiento: {len(sin_avance)}"
)

st.dataframe(
    pd.DataFrame(
        {"Actividades pendientes de registrar": sin_avance}
    )
)
# ----------------------------------------------------------
# Añadido por avances con chatgpt
total_actividades = len(df_gantt)

actividades_reportadas = (
    df_avances["Tarea"]
    .nunique()
)

porcentaje_cobertura = (
    actividades_reportadas
    / total_actividades
    * 100
)

st.subheader("📊 Cobertura del Seguimiento")

c1, c2, c3 = st.columns(3)

c1.metric(
    "Actividades GANTT",
    total_actividades
)

c2.metric(
    "Con Avance",
    actividades_reportadas
)

c3.metric(
    "Cobertura",
    f"{porcentaje_cobertura:.1f}%"
)
# ------------------------------------------------#
#st.write("Columnas Avances")
#st.write(df_avances.columns.tolist())

#st.write("Columnas Gantt")
#st.write(df_gantt.columns.tolist())

# agregado de chatgpt
opciones_tareas = (
    df_gantt["EDT"].astype(str)
    + " - "
    + df_gantt["Nombre"].astype(str)
).tolist()

# --- Formulario de registro ---
st.header("Registro Diario de Avances")

#tarea = st.text_input("Tarea")
tarea = st.selectbox(
    "Actividad",
    opciones_tareas
)
edt = tarea.split(" - ")[0]
nombre_tarea = tarea.split(" - ", 1)[1]

#st.write("EDT:", edt)
#st.write("Actividad:", nombre_tarea)

responsable = st.text_input("Responsable")
fecha_inicio = st.date_input("Fecha Inicio")
fecha_fin = st.date_input("Fecha Fin")
avance = st.slider("% Avance", 0, 100, 0)
observaciones = st.text_area("Observaciones")
estado = st.selectbox("Estado", ["Pendiente", "En curso", "Terminado"])

#if st.button("Guardar avance"):
    #sheet.append_row([tarea, responsable, str(fecha_inicio), str(fecha_fin),
                      #avance, observaciones, estado])
    #st.success("✅ Avance registrado correctamente en Google Sheets")
if st.button("Guardar avance"):
    try:
        hoja_avances.append_row([
            tarea,
            responsable,
            str(fecha_inicio),
            str(fecha_fin),
            avance,
            observaciones,
            estado
        ])

        st.success("✅ Avance registrado correctamente")

    except Exception as e:
        st.error(f"Error: {e}")
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
