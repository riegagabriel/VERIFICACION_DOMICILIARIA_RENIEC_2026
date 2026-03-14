# ====================================================
# TAB 1
# ====================================================
with tab1:

    st.subheader("Indicadores")

    if not value_box.empty:

        indicadores = dict(zip(value_box["Variable"], value_box["Valor"]))

        dnis = indicadores.get("ciudadanos_veri", 0)
        deps = indicadores.get("departamentos", 0)
        provs = indicadores.get("provincias", 0)
        dist = indicadores.get("distritos", 0)
        fechas = indicadores.get("fecha", 0)
        personal = indicadores.get("encuestadores", 0)

    else:

        dnis = deps = provs = dist = fechas = personal = 0

    col1,col2,col3,col4,col5,col6 = st.columns(6)

    col1.metric("🆔 Ciudadanos Verificados", f"{int(dnis):,}")
    col2.metric("🗺️ Departamentos", int(deps))
    col3.metric("🏛️ Provincias", int(provs))
    col4.metric("📍 Distritos", int(dist))
    col5.metric("🗓️ Jornadas", int(fechas))
    col6.metric("👷 Personal", int(personal))

    st.markdown("---")

# ========================
# FILTROS
# ========================

    if not tabla_distrito.empty:

        col1, col2 = st.columns(2)

        with col1:

            deptos = ["Todos"] + sorted(tabla_distrito["REG"].unique())

            depto = st.selectbox(
                "Departamento",
                deptos,
                key="depto_tab1"
            )

        with col2:

            if depto == "Todos":
                distritos = sorted(tabla_distrito["DIST"].unique())
            else:
                distritos = sorted(
                    tabla_distrito[tabla_distrito["REG"] == depto]["DIST"].unique()
                )

            distrito = st.selectbox(
                "Distrito",
                ["Todos"] + distritos,
                key="dist_tab1"
            )

        df_filtrado = tabla_distrito.copy()

        if depto != "Todos":
            df_filtrado = df_filtrado[df_filtrado["REG"] == depto]

        if distrito != "Todos":
            df_filtrado = df_filtrado[df_filtrado["DIST"] == distrito]

    else:

        df_filtrado = pd.DataFrame()

    st.markdown("---")
