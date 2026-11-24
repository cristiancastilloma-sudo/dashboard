import streamlit as st
import pandas as pd
import glob

st.set_page_config(page_title="Mi Dashboard - Sell Out", layout="wide")
st.title("Mi Dashboard - Bienvenido, Cristian Camilo Castillo")
st.subheader("Sell Out 2025 vs 2026 - SURTIDORA QUINDIO")

@st.cache_data
def cargar():
    archivos = glob.glob("*.xlsx")
    df = pd.read_excel(archivos[0], sheet_name="Export")
    df.columns = [c.strip() for c in df.columns]
    df["FECHA"] = pd.to_datetime(df["FECHA"])
    return df

df = cargar()

st.sidebar.header("Filtros")

anos = st.sidebar.multiselect("Año", sorted(df["AÑO"].unique()), default=sorted(df["AÑO"].unique()))
unidades = st.sidebar.multiselect("Unidad de Negocio", sorted(df["UNIDAD DE NEGOCIO"].unique()), default=sorted(df["UNIDAD DE NEGOCIO"].unique()))
categorias = st.sidebar.multiselect("Categoría", sorted(df["CATEGORIA"].unique()))
vendedores = st.sidebar.multiselect("Vendedor", sorted(df["VENDEDOR"].unique()))
pdvs = st.sidebar.multiselect("Punto de Venta", sorted(df["PUENTO DE VENTA"].unique()))

dff = df[df["AÑO"].isin(anos)]
if unidades:
    dff = dff[dff["UNIDAD DE NEGOCIO"].isin(unidades)]
if categorias:
    dff = dff[dff["CATEGORIA"].isin(categorias)]
if vendedores:
    dff = dff[dff["VENDEDOR"].isin(vendedores)]
if pdvs:
    dff = dff[dff["PUENTO DE VENTA"].isin(pdvs)]

total = dff["Evacuación $"].sum()
c1, c2, c3 = st.columns(3)
c1.metric("Ventas Totales", f"${total/1_000_000:,.1f} M")
c2.metric("Registros", f"{len(dff):,}")
c3.metric("Puntos de Venta", f"{dff['PUENTO DE VENTA'].nunique():,}")

st.markdown("### Ventas Mes a Mes")
mensual = dff.groupby([dff["FECHA"].dt.to_period("M").astype(str), "AÑO"])["Evacuación $"].sum().reset_index()
st.line_chart(mensual, x="FECHA", y="Evacuación $", color="AÑO")

col1, col2 = st.columns(2)
with col1:
    st.markdown("### Ventas por Categoría")
    st.bar_chart(dff.groupby("CATEGORIA")["Evacuación $"].sum().sort_values(ascending=False).head(10))
with col2:
    st.markdown("### Ventas por Vendedor")
    st.bar_chart(dff.groupby("VENDEDOR")["Evacuación $"].sum().sort_values(ascending=False).head(10))

st.markdown("### Top Puntos de Venta")
st.dataframe(dff.groupby("PUENTO DE VENTA")["Evacuación $"].sum().sort_values(ascending=False).head(20).reset_index(), use_container_width=True)
