import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Mi Dashboard", layout="wide")

st.markdown("""
<style>
.header {background:#1E5B2E; color:white; padding:14px 20px; border-radius:12px; display:flex; justify-content:space-between; align-items:center}
.header b {font-size:22px}
.kpi {background:white; border-left:8px solid #2E9E4A; border-radius:12px; padding:16px; box-shadow:0 2px 8px #00000015}
.kpi.red {border-left-color:#D32F2F}
.card {background:white; border-radius:12px; padding:16px; box-shadow:0 2px 8px #00000015}
.resumen {background:#2E9E4A; color:white; border-radius:10px; padding:14px}
</style>
""", unsafe_allow_html=True)

df = pd.read_excel("Base limpia Sell Out.xlsx")
df.columns = [str(c).strip().upper() for c in df.columns]

COL_VALOR = None
for c in df.columns:
    if any(x in c for x in ["VALOR", "VENTA", "TOTAL", "MONTO", "IMPORTE", "PRECIO"]):
        COL_VALOR = c
        break
if COL_VALOR is None:
    COL_VALOR = df.columns[-1]
df[COL_VALOR] = pd.to_numeric(df[COL_VALOR], errors="coerce").fillna(0)
# --- HEADER VERDE ---
st.markdown('<div class="header"><div><b>📊 Mi Dashboard</b> &nbsp;|&nbsp; Bienvenido, Cristian Camilo Castillo - Sell Out 2025 vs 2026</div><div>🔔 ⚙️ CC</div></div>', unsafe_allow_html=True)
st.write("")

# --- MENU LATERAL ---
with st.sidebar:
    st.markdown("### 📊 SELL OUT\nv2026.1.0")
    st.write("**▦ Panel**")
    st.write("📋 Chequeos")
    st.write("📄 Hoja de Vida PDV")
    st.write("☰ Tareas")
    st.write("📢 Novedades")
    st.write("🔍 Consulta Producto")
    st.write("📊 Reportes")
    st.write("❓ Ayuda & Soporte")
    if "DISTRIBUIDORA" in df.columns:
        distribuidora = st.selectbox("Distribuidora", ["Todas"] + sorted(df["DISTRIBUIDORA"].astype(str).unique()))
        if distribuidora != "Todas":
            df = df[df["DISTRIBUIDORA"].astype(str) == distribuidora]

# --- CALCULOS ---
df_2025 = df[df["AÑO"] == 2025] if "AÑO" in df.columns else df.iloc[0:0]
df_2026 = df[df["AÑO"] == 2026] if "AÑO" in df.columns else df.iloc[0:0]
v2025 = df_2025[COL_VALOR].sum()
v2026 = df_2026[COL_VALOR].sum()
var = ((v2026 - v2025) / v2025 * 100) if v2025 else 0
pdv = df["PUNTO DE VENTA"].nunique() if "PUNTO DE VENTA" in df.columns else 0

# --- 4 CUADROS DE ARRIBA ---
c1, c2, c3, c4 = st.columns(4)
with c1: st.markdown(f'<div class="kpi"><small>Ventas 2025</small><h2>${v2025/1e6:,.0f} M</h2><span style="color:green">↗ vs 2024</span></div>', unsafe_allow_html=True)
with c2: st.markdown(f'<div class="kpi"><small>Ventas 2026 Ene-Oct</small><h2>${v2026/1e6:,.0f} M</h2><span style="color:green">↗ YTD</span></div>', unsafe_allow_html=True)
with c3: st.markdown(f'<div class="kpi red"><small>Variación Ene-Oct</small><h2>{var:.1f}%</h2><span style="color:red">↘ vs 2025</span></div>', unsafe_allow_html=True)
with c4: st.markdown(f'<div class="kpi"><small>PDVs Activos</small><h2>{pdv}</h2><span style="color:green">● nuevos en 2026</span></div>', unsafe_allow_html=True)
st.write("")
if "MES" in df.columns and "AÑO" in df.columns:
    mensual = df.groupby(["AÑO","MES"])[COL_VALOR].sum().reset_index()
    fig = px.line(mensual, x="MES", y=COL_VALOR, color="AÑO", markers=True)
    st.plotly_chart(fig, use_container_width=True)
    col1, col2 = st.columns(2)
with col1:
    st.markdown('<div class="card"><h3>Ventas por Unidad</h3></div>', unsafe_allow_html=True)
    if "UNIDAD DE NEGOCIO" in df.columns:
        dona = df.groupby("UNIDAD DE NEGOCIO")[COL_VALOR].sum().reset_index()
        fig2 = px.pie(dona, names="UNIDAD DE NEGOCIO", values=COL_VALOR, hole=0.6)
        st.plotly_chart(fig2, use_container_width=True)
with col2:
    st.markdown('<div class="card"><h3>Top Puntos de Venta</h3></div>', unsafe_allow_html=True)
    if "PUNTO DE VENTA" in df.columns:
        top = df_2026.groupby("PUNTO DE VENTA")[COL_VALOR].sum().sort_values(ascending=False).head(3)
        st.dataframe(top)
    st.markdown(f'<div class="resumen"><b>Resumen Ejecutivo</b><br>Variacion {var:.1f}% frente a 2025. Con {pdv} puntos activos.</div>', unsafe_allow_html=True)
