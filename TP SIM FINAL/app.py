import streamlit as st
import pandas as pd
import random
import math

# --- FUNCIONES ESTADÍSTICAS ---
def generar_llegada_rnd(media):
    rnd = random.random()
    tiempo = -media * math.log(1 - rnd)
    return rnd, tiempo

def generar_uniforme_rnd(min_t, max_t):
    rnd = random.random()
    tiempo = min_t + rnd * (max_t - min_t)
    return rnd, tiempo

# --- MOTOR DE SIMULACIÓN ---
def simular_sistema(dias, media_llegadas, atencion_min, atencion_max, reparacion_min, reparacion_max, stock_inicial):
    eventos_tabla = []
    registro_picos_globales = [] 
    
    total_tiempo_bruto_reparacion = 0.0 # Acumulador del tiempo real (Fin - Inicio)
    total_zapatos_reparados_global = 0
    max_cola_global = 0
    
    for dia in range(1, dias + 1):
        reloj = 0.0
        estado_emp = "Libre" 
        cola = 0
        zapatos_listos = stock_inicial
        zapatos_a_reparar = 0
        tiempo_remanente_rep = 0.0
        inicio_reparacion_actual = 0.0 # <--- NUEVA VARIABLE: Guarda cuándo empezó el zapato actual
        
        rnd_lleg, t_lleg = generar_llegada_rnd(media_llegadas)
        prox_llegada = t_lleg
        fin_atencion = float('inf')
        fin_reparacion = float('inf')
        
        corte_llegadas = 480.0
        
        if dia == 1:
            eventos_tabla.append({
                "Reloj": round(reloj, 2),
                "Evento": "Inicio",
                "RND Lleg.": round(rnd_lleg, 4),
                "T. Lleg.": round(t_lleg, 2),
                "Próx. Lleg.": round(prox_llegada, 2),
                "RND Atenc.": "-",
                "T. Atenc.": "-",
                "Fin Atenc.": "-",
                "RND Tipo": "-",
                "RND Rep.": "-",
                "T. Rep.": "-",
                "Fin Rep.": "-",
                "Estado Emp.": estado_emp,
                "Estado Cliente": "-",
                "Estado Zapato": "10 Listos",
                "Cola": cola,
                "Zapatos Listos": zapatos_listos,
                "A Reparar": zapatos_a_reparar,
                "Remanente Rep.": round(tiempo_remanente_rep, 2),
                "Inicio Rep. Actual": "-",
                "Acum. T. Rep.": round(total_tiempo_bruto_reparacion, 2),
                "Cont. Rep.": total_zapatos_reparados_global
            })
        
        while True:
            rnd_lleg = rnd_atenc = rnd_tipo = rnd_rep = "-"
            t_lleg = t_atenc = t_rep = "-"
            est_cliente = "-"
            est_zapato = "-"
            
            min_tiempo = min(prox_llegada, fin_atencion, fin_reparacion)
            
            if min_tiempo == float('inf'):
                break 
                
            reloj = min_tiempo
            evento_actual = ""
            
            # --- LLEGADA DE CLIENTE ---
            if reloj == prox_llegada:
                evento_actual = "Llegada Cliente"
                est_cliente = "Llega a Zapatería"
                
                rnd_lleg, t_lleg = generar_llegada_rnd(media_llegadas)
                prox_llegada = reloj + t_lleg
                if prox_llegada > corte_llegadas:
                    prox_llegada = float('inf') 
                    
                if estado_emp == "Libre":
                    estado_emp = "Atendiendo"
                    rnd_atenc, t_atenc = generar_uniforme_rnd(atencion_min, atencion_max)
                    fin_atencion = reloj + t_atenc
                    est_cliente = "Siendo Atendido"
                    
                elif estado_emp == "Reparando":
                    tiempo_remanente_rep = fin_reparacion - reloj
                    estado_emp = "Atendiendo"
                    fin_reparacion = float('inf')
                    rnd_atenc, t_atenc = generar_uniforme_rnd(atencion_min, atencion_max)
                    fin_atencion = reloj + t_atenc
                    est_zapato = "Reparación Pausada"
                    est_cliente = "Siendo Atendido"
                    
                elif estado_emp == "Atendiendo":
                    cola += 1
                    est_cliente = "Pasa a la Cola"
                    
                    if cola > max_cola_global:
                        max_cola_global = cola
                        registro_picos_globales = [{
                            "Día": dia, "Reloj": round(reloj, 2), "Evento": evento_actual,
                            "Estado Cliente": est_cliente, "Cola": cola
                        }]
                    elif cola == max_cola_global and cola > 0:
                        registro_picos_globales.append({
                            "Día": dia, "Reloj": round(reloj, 2), "Evento": evento_actual,
                            "Estado Cliente": est_cliente, "Cola": cola
                        })
                        
            # --- FIN DE ATENCIÓN ---
            elif reloj == fin_atencion:
                evento_actual = "Fin Atención"
                
                rnd_tipo = random.random() 
                if rnd_tipo < 0.5:
                    if zapatos_listos > 0:
                        zapatos_listos -= 1 
                        est_cliente = "Retira Zapato"
                        est_zapato = "Entregado al Cliente"
                    else:
                        est_cliente = "Se va vacío (Sin stock)"
                else:
                    zapatos_a_reparar += 1 
                    est_cliente = "Deja Zapato"
                    est_zapato = "A Reparar (Al Canasto)"
                    
                if cola > 0:
                    cola -= 1
                    rnd_atenc, t_atenc = generar_uniforme_rnd(atencion_min, atencion_max)
                    fin_atencion = reloj + t_atenc
                else:
                    fin_atencion = float('inf')
                    if zapatos_a_reparar > 0:
                        estado_emp = "Reparando"
                        if tiempo_remanente_rep > 0:
                            # Retoma una reparación pausada, el Inicio NO cambia
                            fin_reparacion = reloj + tiempo_remanente_rep
                            tiempo_remanente_rep = 0.0
                            est_zapato = "Retoma Reparación"
                        else:
                            # Agarra un zapato nuevo, seteamos el Inicio
                            inicio_reparacion_actual = reloj
                            rnd_rep, t_rep = generar_uniforme_rnd(reparacion_min, reparacion_max)
                            fin_reparacion = reloj + t_rep
                            est_zapato = "Inicia Reparación"
                    else:
                        estado_emp = "Libre"
                        
            # --- FIN DE REPARACIÓN ---
            elif reloj == fin_reparacion:
                evento_actual = "Fin Reparación"
                zapatos_a_reparar -= 1
                zapatos_listos += 1
                total_zapatos_reparados_global += 1
                
                # CÁLCULO DEL TIEMPO BRUTO DE ESTE ZAPATO (Fin - Inicio)
                tiempo_bruto_este_zapato = reloj - inicio_reparacion_actual
                total_tiempo_bruto_reparacion += tiempo_bruto_este_zapato
                
                est_zapato = "Reparado (Pasa a Listos)"
                
                if zapatos_a_reparar > 0:
                    # Arranca a reparar el siguiente zapato inmediatamente
                    inicio_reparacion_actual = reloj
                    rnd_rep, t_rep = generar_uniforme_rnd(reparacion_min, reparacion_max)
                    fin_reparacion = reloj + t_rep
                    est_zapato = "Inicia Siguiente Reparación"
                else:
                    fin_reparacion = float('inf')
                    estado_emp = "Libre"
            
            if dia == 1:
                eventos_tabla.append({
                    "Reloj": round(reloj, 2),
                    "Evento": evento_actual,
                    "RND Lleg.": round(rnd_lleg, 4) if rnd_lleg != "-" else "-",
                    "T. Lleg.": round(t_lleg, 2) if t_lleg != "-" else "-",
                    "Próx. Lleg.": round(prox_llegada, 2) if prox_llegada != float('inf') else "-",
                    "RND Atenc.": round(rnd_atenc, 4) if rnd_atenc != "-" else "-",
                    "T. Atenc.": round(t_atenc, 2) if t_atenc != "-" else "-",
                    "Fin Atenc.": round(fin_atencion, 2) if fin_atencion != float('inf') else "-",
                    "RND Tipo": round(rnd_tipo, 4) if rnd_tipo != "-" else "-",
                    "RND Rep.": round(rnd_rep, 4) if rnd_rep != "-" else "-",
                    "T. Rep.": round(t_rep, 2) if t_rep != "-" else "-",
                    "Fin Rep.": round(fin_reparacion, 2) if fin_reparacion != float('inf') else "-",
                    "Estado Emp.": estado_emp,
                    "Estado Cliente": est_cliente,
                    "Estado Zapato": est_zapato,
                    "Cola": cola,
                    "Zapatos Listos": zapatos_listos,
                    "A Reparar": zapatos_a_reparar,
                    "Remanente Rep.": round(tiempo_remanente_rep, 2),
                    "Inicio Rep. Actual": round(inicio_reparacion_actual, 2) if estado_emp == "Reparando" or tiempo_remanente_rep > 0 else "-",
                    "Acum. T. Rep.": round(total_tiempo_bruto_reparacion, 2),
                    "Cont. Rep.": total_zapatos_reparados_global
                })
                
            if reloj >= corte_llegadas and cola == 0 and zapatos_a_reparar == 0 and estado_emp != "Atendiendo":
                break

    # --- CÁLCULO DE PROMEDIO CORRECTO ---
    promedio_reparacion = 0
    if total_zapatos_reparados_global > 0:
        promedio_reparacion = total_tiempo_bruto_reparacion / total_zapatos_reparados_global

    return round(promedio_reparacion, 4), max_cola_global, total_tiempo_bruto_reparacion, total_zapatos_reparados_global, eventos_tabla, registro_picos_globales

# ==========================================
# INTERFAZ WEB CON STREAMLIT
# ==========================================

st.set_page_config(page_title="Simulador de Zapatería", layout="wide")

st.title("👞 Simulador de Sistema de Colas: Zapatería")
st.markdown("---")

st.sidebar.header("⚙️ Parámetros de Simulación")
dias_simulacion = st.sidebar.number_input("Días a simular", min_value=1, value=1000, step=10)

st.sidebar.subheader("Tiempos del Sistema (minutos)")
llegadas_media = st.sidebar.number_input("Media llegadas (Exp)", min_value=1, value=20)

col1, col2 = st.sidebar.columns(2)
with col1:
    atencion_min = st.number_input("Atención Mín.", min_value=1, value=3)
    reparacion_min = st.number_input("Reparación Mín.", min_value=1, value=10)
with col2:
    atencion_max = st.number_input("Atención Máx.", min_value=1, value=4)
    reparacion_max = st.number_input("Reparación Máx.", min_value=1, value=20)

stock_inicial = st.sidebar.number_input("Stock inicial zapatos", min_value=0, value=10)

if st.button("🚀 Ejecutar Simulación", type="primary"):
    
    with st.spinner("Simulando los días solicitados..."):
        prom_rep, max_cola, t_acum_rep, total_zapatos, tabla_eventos, picos_cola = simular_sistema(
            dias_simulacion, llegadas_media, atencion_min, atencion_max, 
            reparacion_min, reparacion_max, stock_inicial
        )
    
    st.success(f"Simulación completada con éxito para {dias_simulacion} días.")
    
    st.subheader("📊 Resultados Finales (Métricas)")
    col_res1, col_res2 = st.columns(2)
    
    with col_res1:
        st.metric(label="Tiempo Promedio de Reparación", value=f"{round(prom_rep, 2)} min")
        st.info(f"**Fórmula:** {round(t_acum_rep, 2)} min acumulados (brutos) ÷ {total_zapatos} zapatos reparados")
        
    with col_res2:
        st.metric(label="Máximo de Clientes en Cola Histórico", value=f"{max_cola} personas")
        st.info("Pico máximo a lo largo de TODA la simulación.")
    
    st.markdown("---")
    
    st.subheader(f"🔍 Análisis del Máximo Histórico de Cola ({max_cola} personas)")
    if len(picos_cola) > 0:
        st.write("Estos son los momentos exactos de la simulación entera donde la cola alcanzó su capacidad máxima:")
        df_picos = pd.DataFrame(picos_cola).head(100)
        st.dataframe(df_picos, hide_index=True)
    else:
        st.info("No hubo personas en cola durante la simulación.")

    st.markdown("---")
    
    st.subheader("📋 Tabla Vector de Estado (Eventos del Día 1)")
    if len(tabla_eventos) > 0:
        df_eventos = pd.DataFrame(tabla_eventos)
        st.dataframe(df_eventos, use_container_width=True, hide_index=True)