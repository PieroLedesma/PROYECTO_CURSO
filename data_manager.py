import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

def get_conn():
    return st.connection("gsheets", type=GSheetsConnection)

def init_files():
    pass

def _safe_read(worksheet, expected_columns):
    conn = get_conn()
    try:
        df = conn.read(worksheet=worksheet, ttl=600)
        df = df.dropna(how="all")
        if "id" not in df.columns:
            return pd.DataFrame(columns=expected_columns)
        # Aseguramos que los IDs sean enteros para evitar errores
        df['id'] = pd.to_numeric(df['id'], errors='coerce').fillna(0).astype(int)
        return df
    except Exception as e:
        if "WorksheetNotFound" in str(e):
            st.error(f"Error: No se encontró la pestaña '{worksheet}' en Google Sheets. Créala.")
        else:
            st.error(f"Error de conexión con Google Sheets: {e}. Por favor, recarga la página.")
        st.stop()

def get_alumnos():
    return _safe_read("Alumnos", ["id", "nombre"])

def save_alumnos(df):
    conn = get_conn()
    conn.update(worksheet="Alumnos", data=df)
    st.cache_data.clear()

def get_eventos():
    return _safe_read("Eventos", ["id", "nombre", "monto_esperado"])

def save_eventos(df):
    conn = get_conn()
    conn.update(worksheet="Eventos", data=df)
    st.cache_data.clear()

def get_pagos():
    return _safe_read("Pagos", ["id", "evento_id", "alumno_id", "fecha", "monto", "modo_pago", "comentario"])

def save_pagos(df):
    conn = get_conn()
    conn.update(worksheet="Pagos", data=df)
    st.cache_data.clear()

def agregar_alumno(nombre):
    df = get_alumnos()
    nuevo_id = 1 if df.empty else df['id'].max() + 1
    nuevo_registro = pd.DataFrame([{"id": nuevo_id, "nombre": nombre}])
    df = pd.concat([df, nuevo_registro], ignore_index=True)
    save_alumnos(df)

def eliminar_alumno(alumno_id):
    df = get_alumnos()
    df = df[df['id'] != alumno_id]
    save_alumnos(df)

def agregar_evento(nombre, monto_esperado):
    df = get_eventos()
    nuevo_id = 1 if df.empty else df['id'].max() + 1
    nuevo_registro = pd.DataFrame([{"id": nuevo_id, "nombre": nombre, "monto_esperado": float(monto_esperado)}])
    df = pd.concat([df, nuevo_registro], ignore_index=True)
    save_eventos(df)
    return nuevo_id

def agregar_pago(evento_id, alumno_id, fecha, monto, modo_pago, comentario):
    df = get_pagos()
    nuevo_id = 1 if df.empty else df['id'].max() + 1
    nuevo_registro = pd.DataFrame([{
        "id": nuevo_id, 
        "evento_id": evento_id, 
        "alumno_id": alumno_id, 
        "fecha": fecha, 
        "monto": float(monto), 
        "modo_pago": modo_pago, 
        "comentario": comentario
    }])
    df = pd.concat([df, nuevo_registro], ignore_index=True)
    save_pagos(df)

def editar_pago(pago_id, fecha, monto, modo_pago, comentario):
    df = get_pagos()
    idx = df.index[df['id'] == pago_id].tolist()
    if idx:
        df.at[idx[0], 'fecha'] = fecha
        df.at[idx[0], 'monto'] = float(monto)
        df.at[idx[0], 'modo_pago'] = modo_pago
        df.at[idx[0], 'comentario'] = comentario
        save_pagos(df)

def eliminar_pago(pago_id):
    df = get_pagos()
    df = df[df['id'] != pago_id]
    save_pagos(df)

def obtener_resumen_evento(evento_id):
    alumnos = get_alumnos()
    pagos = get_pagos()
    evento = get_eventos()[get_eventos()['id'] == evento_id].iloc[0]
    
    pagos_evento = pagos[pagos['evento_id'] == evento_id]
    
    monto_por_alumno = pagos_evento.groupby('alumno_id')['monto'].sum().reset_index()
    
    # Extraemos modo_pago y comentario del último pago registrado (mayor ID)
    ultimos_detalles = pagos_evento.sort_values('id').groupby('alumno_id').tail(1)[['alumno_id', 'modo_pago', 'comentario']]
    
    if monto_por_alumno.empty:
        alumnos_con_pagos = pd.DataFrame(columns=['alumno_id', 'monto_pagado', 'modo_pago', 'comentario'])
    else:
        alumnos_con_pagos = monto_por_alumno.rename(columns={'monto': 'monto_pagado'})
        alumnos_con_pagos = pd.merge(alumnos_con_pagos, ultimos_detalles, on='alumno_id', how='left')
        
    resumen = pd.merge(alumnos, alumnos_con_pagos, left_on='id', right_on='alumno_id', how='left')
    resumen['monto_pagado'] = resumen['monto_pagado'].fillna(0)
    resumen['modo_pago'] = resumen['modo_pago'].fillna("-")
    resumen['comentario'] = resumen['comentario'].fillna("")
    
    monto_esperado = evento['monto_esperado']
    
    if monto_esperado > 0:
        resumen['estado'] = resumen['monto_pagado'].apply(lambda x: 'Pagado' if x >= monto_esperado else ('Abono' if x > 0 else 'Pendiente'))
    else:
        resumen['estado'] = resumen['monto_pagado'].apply(lambda x: 'Pagado' if x > 0 else 'Pendiente')
        
    return resumen
