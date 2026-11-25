import streamlit as st
import pandas as pd
import plotly.express as px
import glob

st.set_page_config(page_title="Dashboard Ventas", layout="wide")
st.title("📊 Dashboard de Ventas")

# --- Cargar datos ---
archivos = glob.glob("*.xlsx") + glob.glob("*.xls") + glob.glob("*.csv")
if not archivos:
    st.error("No encontré ningún archivo Excel o CSV.")
    st.stop()

archivo = archivos[0]
st.caption(f"Archivo cargado: {archivo}")

if archivo.endswith(".csv"):
    df = pd.read_csv(archivo)
else:
    df = pd.read_excel(archivo)

df.columns = [str(c).strip() for c in df.columns]
# --- Detectar columnas ---
def buscar_col(palabras):
    for c in df.columns:
        cl = c.lower()
        for p in palabras:
            if p in cl:
                return c
    return None

col_valor = buscar_col(["valor", "venta", "total", "monto", "neto"])
col_cli = buscar_col(["cliente", "pdv", "punto", "negocio", "razon"])
col_vend = buscar_col(["vendedor", "asesor", "vend"])
col_cat = buscar_col(["categoria", "categoría", "linea", "línea", "marca"])

if col_valor is None:
    st.error(f"No encontré columna de valor. Columnas: {list(df.columns)}")
    st.stop()

df[col_valor] = pd.to_numeric(df[col_valor], errors="coerce").fillna(0)
# --- Filtros ---
st.sidebar.header("Filtros")

if col_cat:
    categorias = ["Todos"] + sorted(df[col_cat].astype(str).unique().tolist())
    cat_sel = st.sidebar.selectbox("Categoría", categorias)
else:
    cat_sel = "Todos"

if col_vend:
    vendedores = ["Todos"] + sorted(df[col_vend].astype(str).unique().tolist())
    vend_sel = st.sidebar.selectbox("Vendedor", vendedores)
else:
    vend_sel = "Todos"

# --- Filtrar ---
df_f = df.copy()
if cat_sel != "Todos" and col_cat:
    df_f = df_f[df_f[col_cat].astype(str) == cat_sel]
if vend_sel != "Todos" and col_vend:
    df_f = df_f[df_f[col_vend].astype(str) == vend_sel]

# --- KPIs - todo afuera del if, sin sangría ---
ventas = df_f[col_valor].sum()
registros = len(df_f)
pdv = df_f[col_cli].nunique() if col_cli else 0
vend_act = df_f[col_vend].nunique() if col_vend else 0
ticket = ventas / registros if registros > 0 else 0
cobertura = pdv / df[col_cli].nunique() * 100 if col_cli and df[col_cli].nunique() > 0 else 0

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Ventas", f"${ventas:,.0f}")
c2.metric("Registros", f"{registros:,}")
c3.metric("PDV", f"{pdv:,}")
c4.metric("Vendedores activos", f"{vend_act:,}")
c5.metric("Ticket promedio", f"${ticket:,.0f}")
st.write(f"Cobertura: {cobertura:.1f}%")
# --- Gráficos ---
st.divider()

if col_cat:
    ventas_cat = df_f.groupby(col_cat)[col_valor].sum().reset_index().sort_values(col_valor, ascending=False)
    fig1 = px.bar(ventas_cat, x=col_cat, y=col_valor, title="Ventas por Categoría")
    st.plotly_chart(fig1, use_container_width=True)

if col_vend:
    ventas_vend = df_f.groupby(col_vend)[col_valor].sum().reset_index().sort_values(col_valor, ascending=False).head(10)
    fig2 = px.bar(ventas_vend, x=col_vend, y=col_valor, title="Top 10 Vendedores")
    st.plotly_chart(fig2, use_container_width=True)

if col_cli:
    top_cli = df_f.groupby(col_cli)[col_valor].sum().reset_index().sort_values(col_valor, ascending=False).head(10)
    fig3 = px.bar(top_cli, x=col_cli, y=col_valor, title="Top 10 Clientes / PDV")
    st.plotly_chart(fig3, use_container_width=True)

st.subheader("Detalle")
st.dataframe(df_f, use_container_width=True)
