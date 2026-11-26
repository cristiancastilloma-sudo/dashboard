import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Sell Out Dashboard", layout="wide")
st.title("📊 Sell Out - Dashboard")

df = pd.read_excel("Base limpia Sell Out.xlsx")
nombres = list(df.columns)
nombres[6] = "PUNTO DE VENTA"
df.columns = nombres
# Filtros
st.sidebar.header("Filtros")
distribuidoras = ["Todas"] + sorted(df["DISTRIBUIDORA"].dropna().unique().tolist())
unidades = ["Todas"] + sorted(df["UNIDAD DE NEGOCIO"].dropna().unique().tolist())
pdvs = ["Todos"] + sorted(df["PUNTO DE VENTA"].dropna().unique().tolist())

f_dist = st.sidebar.selectbox("Distribuidora", distribuidoras)
f_uni = st.sidebar.selectbox("Unidad de Negocio", unidades)
f_pdv = st.sidebar.selectbox("Punto de Venta", pdvs)

dff = df.copy()
if f_dist != "Todas":
    dff = dff[dff["DISTRIBUIDORA"] == f_dist]
if f_uni != "Todas":
    dff = dff[dff["UNIDAD DE NEGOCIO"] == f_uni]
if f_pdv != "Todos":
    dff = dff[dff["PUNTO DE VENTA"] == f_pdv]
    # Ventas por año
ventas_2026 = dff[dff["AÑO"] == 2026]["Evacuación $"].sum()
ventas_2025 = dff[dff["AÑO"] == 2025]["Evacuación $"].sum()
crecimiento = ((ventas_2026 - ventas_2025) / ventas_2025 * 100) if ventas_2025 != 0 else 0
num_pdvs = dff["PUNTO DE VENTA"].nunique()

c1, c2, c3 = st.columns(3)
c1.metric("Ventas 2026", f"${ventas_2026/1e6:.1f} M")
c2.metric("Crecimiento vs 2025", f"{crecimiento:.1f}%")
c3.metric("Puntos de Venta", f"{num_pdvs}")

# Gráfico por mes
mensual = dff.groupby(["MES", "AÑO"])["Evacuación $"].sum().reset_index()
fig = px.bar(mensual, x="MES", y="Evacuación $", color="AÑO", barmode="group", title="Ventas por Mes - 2025 vs 2026")
st.plotly_chart(fig, use_container_width=True)
# Top PDVs
top = dff.groupby("PUNTO DE VENTA")["Evacuación $"].sum().sort_values(ascending=False).head(10).reset_index()
fig2 = px.bar(top, x="Evacuación $", y="PUNTO DE VENTA", orientation="h", title="Top 10 Puntos de Venta")
st.plotly_chart(fig2, use_container_width=True)

st.subheader("Detalle")
st.dataframe(dff)
