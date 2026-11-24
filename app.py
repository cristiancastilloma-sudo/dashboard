import streamlit as st
import pandas as pd
import glob
import plotly.express as px

st.set_page_config(page_title="Análisis Zona Centro Sur", layout="wide")
st.title("📊 Análisis Zona Centro Sur")
st.caption("Sell Out 2025 vs 2026 - Comparativo Mensual")

@st.cache_data
def cargar():
    archivos = glob.glob("*.xlsx")
    df = pd.read_excel(archivos[0])
    df.columns = [c.strip() for c in df.columns]
    col_fecha = [c for c in df.columns if 'fecha' in c.lower()][0]
    df[col_fecha] = pd.to_datetime(df[col_fecha], errors='coerce')
    df['Año'] = df[col_fecha].dt.year
    df['Mes_Num'] = df[col_fecha].dt.month
    df['Mes'] = df[col_fecha].dt.strftime('%Y-%m')
    col_zona = [c for c in df.columns if 'zona' in c.lower()]
    if col_zona:
        df[col_zona[0]] = df[col_zona[0]].astype(str).str.strip()
    return df, col_fecha, col_zona

df, col_fecha, col_zona = cargar()
col_vend = [c for c in df.columns if 'vendedor' in c.lower() or 'asesor' in c.lower()]
col_un = [c for c in df.columns if 'unidad' in c.lower() or 'negocio' in c.lower()]
col_cat = [c for c in df.columns if 'categoria' in c.lower()]
col_cli = [c for c in df.columns if 'cliente' in c.lower() or 'punto' in c.lower() or 'razon' in c.lower()]
col_valor = [c for c in df.columns if 'valor' in c.lower() or 'venta' in c.lower() or 'total' in c.lower()][0]
st.sidebar.header("🔎 Filtros")
años = sorted(df['Año'].dropna().unique().tolist())
año_sel = st.sidebar.selectbox("Año", ["Todos"] + años)

vend_sel = "Todos"
if col_vend:
    vendedores = sorted(df[col_vend[0]].dropna().unique().tolist())
    vend_sel = st.sidebar.selectbox("Vendedor", ["Todos"] + vendedores)

zona_sel = "Todos"
if col_zona:
    zonas = sorted(df[col_zona[0]].dropna().unique().tolist())
    zona_sel = st.sidebar.selectbox("Zona", ["Todos"] + zonas)

un_sel = "Todos"
if col_un:
    unidades = sorted(df[col_un[0]].dropna().unique().tolist())
    un_sel = st.sidebar.selectbox("Unidad de Negocio", ["Todos"] + unidades)

cat_sel = "Todos"
if col_cat:
    cats = sorted(df[col_cat[0]].dropna().unique().tolist())
    cat_sel = st.sidebar.selectbox("Categoría", ["Todos"] + cats)

df_f = df.copy()
if año_sel != "Todos":
    df_f = df_f[df_f['Año'] == año_sel]
if vend_sel != "Todos":
    df_f = df_f[df_f[col_vend[0]] == vend_sel]
if zona_sel != "Todos":
    df_f = df_f[df_f[col_zona[0]] == zona_sel]
if un_sel != "Todos":
    df_f = df_f[df_f[col_un[0]] == un_sel]
if cat_sel != "Todos":
    df_f = df_f[df_f[col_cat[0]] == cat_sel]
    ventas = df_f[col_valor].sum()
registros = len(df_f)
pdv = df_f[col_cli[0]].nunique() if col_cli else 0
vend_act = df_f[col_vend[0]].nunique() if col_vend else 0
ticket = ventas / registros if registros>0 else 0

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("💰 Ventas Totales", f"${ventas:,.1f} M")
k2.metric("📦 Registros", f"{registros:,}")
k3.metric("🏪 Puntos de Venta", f"{pdv:,}")
k4.metric("👤 Vendedores Activos", f"{vend_act}")
k5.metric("🎯 Ticket Promedio", f"${ticket:,.0f}")

st.subheader("📈 Ventas por Mes - Comparación Año vs Mes")
mensual = df_f.groupby(['Año','Mes_Num']).agg({col_valor:'sum'}).reset_index().sort_values(['Año','Mes_Num'])
fig = px.line(mensual, x='Mes_Num', y=col_valor, color='Año', markers=True, labels={'Mes_Num':'Mes (1=Ene, 12=Dic)', col_valor:'Ventas'})
fig.update_xaxes(dtick=1)
st.plotly_chart(fig, use_container_width=True)
c_izq, c_der = st.columns(2)
if col_cli:
    with c_izq:
        st.subheader("🏆 Top 5 Clientes")
        top5 = df_f.groupby(col_cli[0])[col_valor].sum().sort_values(ascending=False).head(5).reset_index()
        fig_top = px.bar(top5, x=col_valor, y=col_cli[0], orientation='h', text_auto=True)
        fig_top.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_top, use_container_width=True)

if col_un:
    with c_der:
        st.subheader("🥧 Participación por Unidad")
        part_un = df_f.groupby(col_un[0])[col_valor].sum().reset_index()
        fig_pie = px.pie(part_un, values=col_valor, names=col_un[0], hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)

c2_izq, c2_der = st.columns(2)
if col_cat:
    with c2_izq:
        st.subheader("🥧 Participación por Categoría")
        part_cat = df_f.groupby(col_cat[0])[col_valor].sum().sort_values(ascending=False).reset_index()
        fig_cat = px.bar(part_cat, x=col_cat[0], y=col_valor, text_auto=True)
        st.plotly_chart(fig_cat, use_container_width=True)

if col_zona:
    with c2_der:
        st.subheader("🥧 Participación por Zona")
        part_z = df_f.groupby(col_zona[0])[col_valor].sum().sort_values(ascending=False).reset_index()
        fig_z = px.bar(part_z, x=col_zona[0], y=col_valor, text_auto=True)
        st.plotly_chart(fig_z, use_container_width=True)

st.subheader("📋 Tabla Mensual")
st.dataframe(mensual, use_container_width=True)
