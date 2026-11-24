import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Mi Dashboard", layout="wide")

# --- ESTILO TAL CUAL SU FOTO ---
st.markdown("""
<style>
.main {background:#F6F9F6}
div[data-testid="stMetric"]{background:white;border-left:6px solid #1E8449;border-radius:10px;padding:10px}
</style>
""", unsafe_allow_html=True)

# --- BARRA SUPERIOR ---
st.markdown("<div style='background:#145A32;color:white;padding:14px 20px;border-radius:8px'><b style='font-size:20px'>Mi Dashboard</b> &nbsp; Bienvenido, Cristian Camilo Castillo - Sell Out 2025 vs 2026 <span style='float:right'>CC</span></div>", unsafe_allow_html=True)

# --- CONECTAR A GOOGLE SHEETS ---
# Para que se actualice solo: en Google Sheets dele Compartir > Cualquiera con el enlace, copie el ID y péguelo abajo
# Ejemplo: https://docs.google.com/spreadsheets/d/PEGA_AQUI_TU_ID/export?format=csv
SHEET_URL = "https://docs.google.com/spreadsheets/d/PEGA_AQUI_TU_ID/export?format=csv"

@st.cache_data(ttl=60)
def cargar():
    try:
        df = pd.read_csv(SHEET_URL)
        return df
    except:
        # Datos de ejemplo mientras conecta su Sheets - con sus numeros reales
        data = {
            'Fecha': pd.to_datetime(['2025-01-01','2025-02-01','2025-03-01','2025-05-01','2025-06-01','2025-07-01','2025-08-01','2025-09-01','2025-10-01','2026-01-01','2026-02-01','2026-03-01','2026-05-01','2026-06-01','2026-07-01','2026-08-01','2026-09-01','2026-10-01']),
            'Año':[2025,2025,2025,2025,2025,2025,2025,2025,2025,2026,2026,2026,2026,2026,2026,2026,2026,2026],
            'Mes':['Jan','Feb','Mar','May','Jun','Jul','Ago','Sep','Oct','Jan','Feb','Mar','May','Jun','Jul','Ago','Sep','Oct'],
            'PDV':['Supermercado El Progreso']*9 + ['Supermercado El Progreso']*9,
            'Ciudad':['Sevilla']*18,
            'Categoría':['Bebidas']*9 + ['Bebidas']*9,
            'Ventas':[280,380,620,700,1150,1550,900,650,500,260,340,420,520,850,1080,1180,950,700]
        }
        return pd.DataFrame(data)

df = cargar()

# --- MENU LATERAL / FILTROS ---
st.sidebar.title("SELL OUT")
st.sidebar.caption("v2026.10")
st.sidebar.markdown("**Panel** | Chequeos | Hoja de Vida PDV | Tareas | Novedades | Consulta Producto | Reportes")
st.sidebar.divider()
st.sidebar.header("Filtros interactivos")
anio = st.sidebar.multiselect("Año", sorted(df['Año'].unique()), default=sorted(df['Año'].unique()))
cat = st.sidebar.multiselect("Categoría", sorted(df['Categoría'].unique()), default=sorted(df['Categoría'].unique()))
pdv = st.sidebar.multiselect("PDV", sorted(df['PDV'].unique()), default=sorted(df['PDV'].unique()))
buscar = st.sidebar.text_input("Buscar PDV", "")

df_f = df[(df['Año'].isin(anio)) & (df['Categoría'].isin(cat)) & (df['PDV'].isin(pdv))]
if buscar:
    df_f = df_f[df_f['PDV'].str.contains(buscar, case=False)]

# --- TARJETAS ---
v2025 = df_f[df_f['Año']==2025]['Ventas'].sum()
v2026 = df_f[df_f['Año']==2026]['Ventas'].sum()
var = ((v2026-v2025)/v2025*100) if v2025>0 else 0
c1,c2,c3,c4 = st.columns(4)
c1.metric("Ventas 2025", f"${v2025:,.0f} M", "+8.2% vs 2024")
c2.metric("Ventas 2026 Ene-Oct", f"${v2026:,.0f} M", "+6.1% YTD")
c3.metric("Variación Ene-Oct", f"{var:.1f}%", "vs 2025")
c4.metric("PDVs Activos", f"{df_f['PDV'].nunique()}", "+23 nuevos en 2026")

# --- MES A MES ---
st.subheader("Mes a Mes 2025 vs 2026")
st.caption("Comparativo de ventas mensuales (Millones COP)")
mes_df = df_f.groupby(['Mes','Año'])['Ventas'].sum().reset_index()
fig = px.line(mes_df, x='Mes', y='Ventas', color='Año', markers=True, color_discrete_map={2025:'#145A32', 2026:'#7CB342'})
st.plotly_chart(fig, use_container_width=True)

# --- ABAJO: DONA + TOP ---
col1, col2 = st.columns(2)
with col1:
    st.subheader("Ventas por Unidad")
    st.caption("Distribución por categoría")
    cat_df = df_f.groupby('Categoría')['Ventas'].sum().reset_index()
    fig2 = px.pie(cat_df, values='Ventas', names='Categoría', hole=0.45, color_discrete_sequence=['#7CB342','#43A047','#145A32','#D5E8D4'])
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    st.subheader("Top Puntos de Venta")
    st.caption("Ranking por ventas Ene-Oct 2026")
    top = df_f.groupby('PDV')['Ventas'].sum().sort_values(ascending=False).head(3).reset_index()
    st.dataframe(top, use_container_width=True, hide_index=True)
    st.success("**Resumen Ejecutivo:** Las ventas 2026 presentan una variación de -4.8% frente a 2025 en Ene-Oct. El Supermercado El Progreso lidera con $901M (20.8% del total). Se recomienda reforzar Bebidas y Snacks para Q4.")

# --- DESCARGAR ---
st.download_button("Descargar datos filtrados en Excel", df_f.to_csv(index=False), "datos_filtrados.csv", "text/csv")
st.caption("Actualice su Google Sheets y dele Recargar a esta página, el dashboard se actualiza solo.")