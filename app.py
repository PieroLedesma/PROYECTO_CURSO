import streamlit as st
import pandas as pd
from datetime import date
from ui_components import apply_custom_css, header
import data_manager as dm

st.set_page_config(
    page_title="Gestor 6to Básico",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Initialize files
dm.init_files()
apply_custom_css()

# Session State for navigation
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Home"
if 'selected_event_id' not in st.session_state:
    st.session_state.selected_event_id = None

# Navigation logic functions
def navigate_to(page, event_id=None):
    st.session_state.current_page = page
    if event_id is not None:
        st.session_state.selected_event_id = event_id
    st.rerun()

# ----------------- VIEWS -----------------

def view_home():
    header("🎓 Gestor 6to Básico")
    st.markdown("<p style='text-align: center; color: #6b7280; margin-bottom: 30px;'>Gestión de cuotas, rifas y eventos del curso</p>", unsafe_allow_html=True)
    
    # Dashboard resumido
    eventos = dm.get_eventos()
    pagos = dm.get_pagos()
    
    total_recaudado = pagos['monto'].sum() if not pagos.empty else 0
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Total Recaudado (Año)", value=f"${total_recaudado:,.0f}")
    with col2:
        st.metric(label="Eventos Activos", value=f"{len(eventos)}")
        
    st.divider()
    
    st.subheader("📋 Eventos y Cuotas")
    if eventos.empty:
        st.info("No hay eventos creados. ¡Crea uno nuevo abajo!")
    else:
        for _, row in eventos.iterrows():
            with st.container():
                cols = st.columns([3, 1])
                cols[0].markdown(f"**{row['nombre']}**<br><small>Monto esperado: ${row['monto_esperado']:,.0f}</small>", unsafe_allow_html=True)
                if cols[1].button("Ver", key=f"btn_ver_{row['id']}"):
                    navigate_to("Evento", event_id=row['id'])
                st.markdown("<hr style='margin: 10px 0; border: 0; border-top: 1px solid #e5e7eb;'>", unsafe_allow_html=True)

    st.write("")
    with st.expander("➕ Crear Nuevo Evento"):
        with st.form("form_nuevo_evento"):
            nombre_ev = st.text_input("Nombre del Evento (Ej: Cuota Anual 2026)")
            monto_ev = st.number_input("Monto Esperado por Alumno ($)", min_value=0, step=1000)
            submitted = st.form_submit_button("Crear Evento")
            if submitted:
                if nombre_ev:
                    dm.agregar_evento(nombre_ev, monto_ev)
                    st.success("Evento creado exitosamente!")
                    st.rerun()
                else:
                    st.error("Ingresa un nombre para el evento.")

    st.write("")
    if st.button("⚙️ Gestionar Alumnos del Curso", use_container_width=True):
        navigate_to("Alumnos")

def view_evento():
    evento_id = st.session_state.selected_event_id
    if evento_id is None:
        navigate_to("Home")
        return
        
    eventos = dm.get_eventos()
    if eventos.empty or evento_id not in eventos['id'].values:
        navigate_to("Home")
        return
        
    evento = eventos[eventos['id'] == evento_id].iloc[0]
    
    if st.button("⬅️ Volver al Inicio"):
        navigate_to("Home")
        
    header(f"🎟️ {evento['nombre']}")
    st.markdown(f"<p style='text-align: center; color: #6b7280;'>Monto Esperado: ${evento['monto_esperado']:,.0f}</p>", unsafe_allow_html=True)
    
    resumen = dm.obtener_resumen_evento(evento_id)
    
    # Metrics Dashboard
    total_recaudado = resumen['monto_pagado'].sum()
    pagados = len(resumen[resumen['estado'] == 'Pagado'])
    pendientes = len(resumen[resumen['estado'] == 'Pendiente'])
    abonos = len(resumen[resumen['estado'] == 'Abono'])
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Recaudado", f"${total_recaudado:,.0f}")
    col2.metric("Pagados", pagados)
    col3.metric("Pendientes", pendientes)
    
    st.divider()
    
    # Tabs para Formulario y Listas
    tab1, tab2, tab3 = st.tabs(["💰 Registrar Pago", "✅ Pagados", "❌ Pendientes"])
    
    with tab1:
        st.subheader("Nuevo Pago")
        alumnos = dm.get_alumnos()
        if alumnos.empty:
            st.warning("⚠️ No hay alumnos registrados. Por favor, ve a Gestionar Alumnos primero.")
            if st.button("Ir a Gestionar Alumnos"):
                navigate_to("Alumnos")
        else:
            with st.form("form_pago", clear_on_submit=True):
                # Opciones de alumnos formateadas
                opciones_alumnos = {row['id']: row['nombre'] for _, row in alumnos.iterrows()}
                alumno_id = st.selectbox("Alumno", options=list(opciones_alumnos.keys()), format_func=lambda x: opciones_alumnos[x])
                
                fecha_pago = st.date_input("Fecha", date.today())
                monto = st.number_input("Monto ($)", min_value=0, step=1000, value=int(evento['monto_esperado']))
                modo_pago = st.selectbox("Modo de Pago", ["Transferencia", "Efectivo"])
                comentario = st.text_input("Comentario (Opcional)")
                
                submit_pago = st.form_submit_button("Guardar Información")
                if submit_pago:
                    if monto > 0:
                        dm.agregar_pago(evento_id, alumno_id, fecha_pago, monto, modo_pago, comentario)
                        st.success(f"Pago de {opciones_alumnos[alumno_id]} registrado!")
                        st.rerun()
                    else:
                        st.error("El monto debe ser mayor a 0.")
                        
        st.write("")
        with st.expander("Ver Últimos Pagos Registrados"):
            pagos = dm.get_pagos()
            pagos_evento = pagos[pagos['evento_id'] == evento_id]
            if pagos_evento.empty:
                st.write("No hay pagos aún.")
            else:
                # Merge with students to show names
                pagos_nombres = pd.merge(pagos_evento, alumnos, left_on='alumno_id', right_on='id', how='left')
                mostrar_df = pagos_nombres[['fecha', 'nombre', 'monto', 'modo_pago', 'comentario']].sort_values(by='fecha', ascending=False)
                st.dataframe(mostrar_df, use_container_width=True, hide_index=True)
                
    with tab2:
        st.subheader("Alumnos que han Pagado (o Abonado)")
        pagados_df = resumen[resumen['estado'].isin(['Pagado', 'Abono'])][['nombre', 'monto_pagado', 'estado']]
        if pagados_df.empty:
            st.info("Nadie ha pagado aún.")
        else:
            st.dataframe(pagados_df, use_container_width=True, hide_index=True)
            
    with tab3:
        st.subheader("Alumnos Pendientes")
        pendientes_df = resumen[resumen['estado'] == 'Pendiente'][['nombre']]
        if pendientes_df.empty:
            st.success("¡Todos han pagado!")
        else:
            st.dataframe(pendientes_df, use_container_width=True, hide_index=True)

def view_alumnos():
    if st.button("⬅️ Volver al Inicio"):
        navigate_to("Home")
        
    header("🧑‍🎓 Gestión de Alumnos")
    st.markdown("<p style='text-align: center; color: #6b7280;'>Lista de estudiantes del 6to Básico</p>", unsafe_allow_html=True)
    
    alumnos = dm.get_alumnos()
    
    col1, col2 = st.columns([2, 1])
    with col1:
        if alumnos.empty:
            st.info("No hay alumnos registrados.")
        else:
            st.dataframe(alumnos[['nombre']], use_container_width=True, hide_index=True)
            
    with col2:
        st.subheader("Agregar")
        with st.form("form_alumno", clear_on_submit=True):
            nuevo_nombre = st.text_input("Nombre y Apellido")
            submit = st.form_submit_button("Agregar")
            if submit:
                if nuevo_nombre:
                    dm.agregar_alumno(nuevo_nombre)
                    st.success("Agregado!")
                    st.rerun()
                else:
                    st.error("Ingresa un nombre.")

# ----------------- ROUTER -----------------
if st.session_state.current_page == "Home":
    view_home()
elif st.session_state.current_page == "Evento":
    view_evento()
elif st.session_state.current_page == "Alumnos":
    view_alumnos()
