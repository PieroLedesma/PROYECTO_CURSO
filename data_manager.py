import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

def get_conn():
    return st.connection("gsheets", type=GSheetsConnection)

def init_files():
    # Ya no necesitamos crear archivos locales.
    # Asumimos que las pestañas "Alumnos", "Eventos" y "Pagos" existen en el Google Sheet.
    pass

def get_alumnos():
    conn = get_conn()
    try:
        df = conn.read(worksheet="Alumnos", ttl=0)
        df = df.dropna(how="all")
        if "id" not in df.columns:
            return pd.DataFrame(columns=["id", "nombre"])
        return df
    except Exception:
        return pd.DataFrame(columns=["id", "nombre"])

def save_alumnos(df):
    conn = get_conn()
    conn.update(worksheet="Alumnos", data=df)

def get_eventos():
    conn = get_conn()
    try:
        df = conn.read(worksheet="Eventos", ttl=0)
        df = df.dropna(how="all")
        if "id" not in df.columns:
            return pd.DataFrame(columns=["id", "nombre", "monto_esperado"])
        return df
    except Exception:
        return pd.DataFrame(columns=["id", "nombre", "monto_esperado"])

def save_eventos(df):
    conn = get_conn()
    conn.update(worksheet="Eventos", data=df)

def get_pagos():
    conn = get_conn()
    try:
        df = conn.read(worksheet="Pagos", ttl=0)
        df = df.dropna(how="all")
        if "id" not in df.columns:
            return pd.DataFrame(columns=["id", "evento_id", "alumno_id", "fecha", "monto", "modo_pago", "comentario"])
        return df
    except Exception:
        return pd.DataFrame(columns=["id", "evento_id", "alumno_id", "fecha", "monto", "modo_pago", "comentario"])

def save_pagos(df):
    conn = get_conn()
    conn.update(worksheet="Pagos", data=df)

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

def obtener_resumen_evento(evento_id):
    alumnos = get_alumnos()
    pagos = get_pagos()
    evento = get_eventos()[get_eventos()['id'] == evento_id].iloc[0]
    
    pagos_evento = pagos[pagos['evento_id'] == evento_id]
    
    # Monto total por alumno en este evento
    monto_por_alumno = pagos_evento.groupby('alumno_id')['monto'].sum().reset_index()
    
    if monto_por_alumno.empty:
        alumnos_con_pagos = pd.DataFrame(columns=['alumno_id', 'monto_pagado'])
    else:
        alumnos_con_pagos = monto_por_alumno.rename(columns={'monto': 'monto_pagado'})
        
    resumen = pd.merge(alumnos, alumnos_con_pagos, left_on='id', right_on='alumno_id', how='left')
    resumen['monto_pagado'] = resumen['monto_pagado'].fillna(0)
    
    monto_esperado = evento['monto_esperado']
    
    # Consideramos pagado si monto_pagado >= monto_esperado (si hay un monto_esperado definido)
    if monto_esperado > 0:
        resumen['estado'] = resumen['monto_pagado'].apply(lambda x: 'Pagado' if x >= monto_esperado else ('Abono' if x > 0 else 'Pendiente'))
    else:
        resumen['estado'] = resumen['monto_pagado'].apply(lambda x: 'Pagado' if x > 0 else 'Pendiente')
        
    return resumen
