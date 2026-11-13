import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import linregress
import plotly.graph_objects as go


# ==========================================
# 🎨 CONFIGURACIÓN DE PÁGINA Y ESTILOS CSS
# ==========================================
st.set_page_config(
    page_title="CineticApp | Fisicoquímica Farmacéutica UdeA",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo CSS personalizado para Dark Mode elegante, fuentes y tarjetas métricas sin recortar
st.markdown("""
<style>
    @import url('[suspicious link removed]');

    html, bosy, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Evitar que los textos y números largos se corten con (...) */
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
        white-space: normal !important;
        text-overflow: unset !important;
        overflow: visible !important;
        word-break: break-word !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.6rem !important;
        font-weight: 700 !important;
        color: #00D2FF
    }

    [dara-testid="stMetricLabel"] {
        font-size: 0.9rem !important;
        color: #94A3B8 !important;
    }

    /* Tarjetas personalizadas de vida útil */
    .metric-card {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 12px;
        paddig: 16px;
        text-align: center;
        box shadow: 0 4px 12px rgba(0, 0, 0, 0.25)
    }
    .mtric-title {
        font-size: 1.4rem;
        color: #00D2FF;
        font-weight: 700;
    }
    .metric-sub {
        font-size: 0.8rem;
        color: #64748B;
        margin-top: 4px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 📊 BARRA LATERAL (SIDEBAR)
# ==========================================
with st.sidebar:
    st.title("🧪 CineticApp")
    st.caption("Fisicoquímica Farmacéutica | UdeA")
    st.divider()

    st.subheader("⚙️Configuración de Datos")
    cargar_ejemplo = st.checkbox("💡 Cargar datos de ejemplo (Reacción Efervescente)", value=False)

    # 📁 NUEVO: Cargar archivo Excel o CSV 
    uploaded_file = st.file_uploader("📁 Cargar matriz de Excel (.xlsx / .csv)", type=["xlsx", "xls", "csv"])

    # 📌 NUEVO: Recomendación de formato de columnas
    st.caption("""
        <div style="font.size: 0.78rem; color: #00D2FF; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">
            Estructura requerida del Excel:
        </div>
        <div style="font-size: 0.78rem; color: #cbd5e1; line-height: 1.5; margin-top: 4px;">
            <b>HOJA 1 (CINÉTICA): </b> Col A = Tiempo, Col B = Concentración.<br> 
            <b>HOJA 2 (ARRHENIUS): </b> Col A = Temp (°C), Col B = Constante <i>k</i>.
        </div>
    </div>
    """, unsafe_allow_html=True) 

    st.divider()
    st.info("📌 **Desarrollado para:** \nEvaluación Cinética, Ecuación de Arrhenius y Ficha de Estabilidad Farmacéutica")
    st.divider()

 #Tarjeta científica del equipo de trabajo
    st.caption("""
        <div style="font-size: 0.8rem; font-weight: 800; color: #cbd5e1; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">
            Desarrollado por:
        </div>
        <div style="font-size: 0.85rem; color: #cbd5e1; line-height: 1.6;">
            D. Carrascal, L. Garzón, L. Tobón y L. Murillo
        </div>
        <div style="font-size: 0.75rem; color: #64748b; margin-top: 10px; font-style: italic; border-top: 1px solid #334155; padding-top: 6px;">
    """, unsafe_allow_html=True)

# ==========================================
# 🏠 ENCABEZADO Y PESTAÑAS PRINCIPALES
# ==========================================
st.title("🧪 Plataforma de Análisis Cinético y Predicción de Estabilidad")
st.markdown("Herramienta interactiva para la determinación de órdenes de reacción, parámetros de Arrhenius y vida útil farmacéutica")

# Pestañas principales de la interfaz
tab_cinética, tab_orden, tab_arrhenius, tab_prediccion = st.tabs([
    " 1. Entrada de Datos & Método Integral",
    " 2. Orden Cinético & Vida Útil",
    " 3. Módulo de Arrhenius",
    " 4. Predicción de Estabilidad"
])

# ==========================================
# 1. ENTRADA DE DATOS Y MÉTODO INTEGRAL
# ==========================================
with tab_cinética:
    st.header("1. Datos Experimentales y Gráficos del Método Integral")
    
    # 🔄 NUEVO: Selectores de Unidades para conversión automática 
    col_u1, col_u2 = st.columns(2)
    with col_u1: 
        unidad_tiempo = st.selectbox( 
            "⏱ Unidad de entrada del tiempo:", 
            ["Minutos (min)", "Segundos (s)", "Horas (h)", "Días (d)", "Semanas (wk)", "Años (yr)"], 
            index=0 
        ) 
        with col_u2: 
            unidad_conc = st.text_input("🧪 Unidad de concentración (ej. M, mg/mL, %):", value="M")

    st.write("Ingresa los datos de **Tiempo ($t$)** y **Concentración ($[A]$)** en la tabla interactiva:")

    # Lógica de carga: 1. Archivo subido > 2. Ejemplo > 3. Tabla en blanco
    df_arr_from_file = None # Variable auxiliar para Arrhenius
   
    if uploaded_file is not None: 
        try: 

            # Leer el archivo sin asumir encabezados fijos
            if uploaded_file.name.endswith('.csv'): 
                df_loaded = pd.read_csv(uploaded_file) 
            else: 
                # Leer libro completo de Excel
                excel_file = pd.ExcelFile(uploaded_file)
                df_loaded = pd.read_excel(excel_file, sheet_name=0, header=None)

            # Si el archivo tiene una segunda hoja, leer datos para Arrhenius 
            if len(excel_file.sheet_names) > 1: 
                df_sheet2 = pd.read_excel(excel_file, sheet_name=1, header=None) 
                c0_arr = pd.to_numeric(df_sheet2.iloc[:, 0], errors='coerce') 
                c1_arr = pd.to_numeric(df_sheet2.iloc[:, 1], errors='coerce') 
                m_arr = ~c0_arr.isna() & ~c1_arr.isna() 
                if m_arr.sum() > 0: 
                    df_arr_from_file = pd.DataFrame({ 
                        "Temperatura (°C)": c0_arr[m_arr].values, 
                        "Constante k": c1_arr[m_arr].values
                    })     

            # Limpieza de datos Cinética (Hoja 1)
            col0_num = pd.to_numeric(df_loaded.iloc[:, 0], errors='coerce') 
            col1_num = pd.to_numeric(df_loaded.iloc[:, 1], errors='coerce')

            # Filtro inteligente: conservar únicamente las filas con 2 datos numéricos válidos 
            mask_valid = ~col0_num.isna() & ~col1_num.isna()

            if mask_valid.sum() > 0: 
                df_init = pd.DataFrame({ 
                    "Tiempo": col0_num[mask_valid].values, 
                    "Concentración": col1_num[mask_valid].values 
                }) 
                st.success(f"✅ ¡Archivo `{uploaded_file.name}` cargado ({len(df_init)} datos numéricos encontrados)!") 
            else: 
                st.warning("⚠️ No se encontraron filas numéricas válidas en las primeras 2 columnas del archivo.") 
                df_init = pd.DataFrame({"Tiempo": [None, None, None, None], "Concentración": [None, None, None, None]}) 
        except Exception as e: 
            st.error(f"⚠️ Error al leer el archivo Excel: {e}") 
            df_init = pd.DataFrame({"Tiempo": [None, None, None, None], "Concentración": [None, None, None, None]}) 
                
            # Tomar las primeras dos columnas 
            df_init = pd.DataFrame({ 
                "Tiempo": df_loaded.iloc[:, 0], 
                "Concentración": df_loaded.iloc[:, 1] 
                }) 
            st.success(f"✅ ¡Archivo `{uploaded_file.name}` cargado con éxito!")
        except Exception as e: 
            st.error(f"⚠️ Error al leer el archivo Excel: {e}") 
            df_init = pd.DataFrame({"Tiempo": [None, None, None, None], "Concentración": [None, None, None, None]}) 
    elif cargar_ejemplo: 
        df_init = pd.DataFrame({ 
            "Tiempo": [0.0, 3.0, 6.0, 9.0, 12.0, 15.0, 18.0, 21.0, 24.0, 27.0, 30.0, 33.0], 
            "Concentración": [0.2500, 0.2112, 0.1801, 0.1545, 0.1317, 0.1118, 0.0961, 0.0823, 0.0705, 0.0598, 0.0514, 0.0447] 
            }) 
    else: 
        df_init = pd.DataFrame({ 
            "Tiempo": [None, None, None, None], 
            "Concentración": [None, None, None, None] 
            })

    df_editor = st.data_editor(df_init, num_rows="dynamic", key="tabla_cinética")

    # Extracción y filtrado de datos válidos 
    t_raw = pd.to_numeric(df_editor.iloc[:, 0], errors='coerce').values 
    A_raw = pd.to_numeric(df_editor.iloc[:, 1], errors='coerce').values 
    mask = ~np.isnan(t_raw) & ~np.isnan(A_raw) & (A_raw > 0) 
    t_ingresado = t_raw[mask] 
    A = A_raw[mask] 
    
    # 🔄 Conversión automática del tiempo a MINUTOS para mantener los cálculos cinéticos estándar 
    factores_tiempo = { 
        "Minutos (min)": 1.0, 
        "Segundos (s)": 1.0 / 60.0, 
        "Horas (h)": 60.0, 
        "Días (d)": 1440.0, 
        "Semanas (wk)": 10080.0, 
        "Años (yr)": 525600.0 
    } 
    factor_t = factores_tiempo[unidad_tiempo] 
    t = t_ingresado * factor_t # El tiempo 't' usado en los cálculos siempre queda en minutos


    if len(t) >= 3:
        # Transformaciones
        ln_A = np.log(A)
        inv_A = 1.0 / A

        # Regresiones lineales para Orden 0, 1 y 2
        res_0 = linregress(t, A)
        res_1 = linregress(t, ln_A)
        res_2 = linregress(t, inv_A)

        r2_0 = res_0.rvalue**2
        r2_1 = res_1.rvalue**2
        r2_2 = res_2.rvalue**2

        st.subheader(" Gráficos por Orden de Reacción")
        g_tab0, g_tab1, g_tab2 = st.tabs(["Orden 0 ([A] vs t)", "Orden 1 (ln[A] vs t)", "Orden 2 (1/[A] vs t)"])

        signo0 = "+" if res_0.intercept >= 0 else ""
        ecuacion0 = f"[A] = {res_0.slope:.6f}·t {signo0} {res_0.intercept:.6f}"

        signo1 = "+" if res_1.intercept >= 0 else ""
        ecuacion1 = f"ln[A] = {res_1.slope:.6f}·t {signo1} {res_1.intercept:.6f}" 

        signo2 = "+" if res_2.intercept >= 0 else ""
        ecuacion2 = f"1/[A] = {res_2.slope:.6f}·t {signo2} {res_2.intercept:.6f}"    

        # --- ORDEN 0 ---
        with g_tab0:
            fig0 = go.Figure()
            fig0.add_trace(go.Scatter(x=t, y=A, mode='markers', name='Datos Esperimentales', marker=dict(size=9, color='#00D2FF')))    
            fig0.add_trace(go.Scatter(x=t, y=res_0.slope*t + res_0.intercept, mode='lines', name=f'Ajuste (R²={r2_0:.4f})', line=dict(color='#FF4B4B', dash='dash')))
            fig0.update_layout(title=f"Orden Cero: {ecuacion0}", xaxis_title="Tiempo (t)", yaxis_title="[A]", template="plotly_dark")
            st.plotly_chart(fig0, width="stretch")
            st.info(f"""
* **Ecuación de la recta:** `{ecuacion0}`
* **Pendiente (m):** {res_0.slope:.6f}
* **Intercepto (b):** {res_0.intercept:.6f}
* **Coenficiente de Determinación (R²):** {r2_0:.4f}
""")

        # --- ORDEN 1 ---
        with g_tab1:
            fig1 = go.Figure()
            fig1.add_trace(go.Scatter(x=t, y=ln_A, mode='markers', name='Datos Esperimentales', marker=dict(size=9, color='#00E676')))    
            fig1.add_trace(go.Scatter(x=t, y=res_1.slope*t + res_1.intercept, mode='lines', name=f'Ajuste (R²={r2_1:.4f})', line=dict(color='#FF4B4B', dash='dash')))
            fig1.update_layout(title=f"Orden Uno: {ecuacion1}", xaxis_title="Tiempo (t)", yaxis_title="ln[A]", template="plotly_dark")
            st.plotly_chart(fig1, width="stretch")
            st.info(f"""
* **Ecuación de la recta:** `{ecuacion1}`
* **Pendiente (m):** {res_1.slope:.6f}
* **Intercepto (b):** {res_1.intercept:.6f}
* **Coenficiente de Determinación (R²):** {r2_1:.4f}
""")       

        # --- ORDEN 2 ---
        with g_tab2:
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=t, y=inv_A, mode='markers', name='Datos Esperimentales', marker=dict(size=9, color='#FFB300')))    
            fig2.add_trace(go.Scatter(x=t, y=res_2.slope*t + res_2.intercept, mode='lines', name=f'Ajuste (R²={r2_0:.4f})', line=dict(color='#FF4B4B', dash='dash')))
            fig2.update_layout(title=f"Orden Dos: {ecuacion2}", xaxis_title="Tiempo (t)", yaxis_title="1 / [A]", template="plotly_dark")
            st.plotly_chart(fig2, width="stretch")
            st.info(f"""
* **Ecuación de la recta:** `{ecuacion2}`
* **Pendiente (m):** {res_2.slope:.6f}
* **Intercepto (b):** {res_2.intercept:.6f}
* **Coenficiente de Determinación (R²):** {r2_2:.4f}
""")
    else:
        st.warning("⚠️ Ingresa al menos 3 filas completas de datos en la tabla para generar los modelos gráficos.") 
    st.divider()

# ==========================================
# 2. ORDEN CINÉTICO Y PARÁMETROS DE VIDA ÚTIL 
# ==========================================
with tab_orden:
    st.warning("⚠️ Completa los datos en la Pestaña 1 para habilitar el cálculo de orden y tiempos de vida útil.")

    if len(t) >= 3:
        st.header("2. Determinación de Orden de Reacción")
        # Selección del modelo ganador
        r2_dict = {"Orden Cero (0)": r2_0, "Orden Uno (1)": r2_1, "Orden Dos (2)": r2_2}
        mejor_orden = max(r2_dict, key=r2_dict.get)
        mejor_r2 = r2_dict[mejor_orden]

        st.subheader(" Comparación de Coeficientes de Determinación (R²)")
        c_r0, c_r1, c_r2 = st.columns(3)
        c_r0.metric("Orden 0 (R²)", f"{r2_0:.4f}")
        c_r1.metric("Orden 1 (R²)", f"{r2_1:.4f}")
        c_r2.metric("Orden 2 (R²)", f"{r2_2:.4f}")

        st.markdown(f""" 
        <div style="background: rgba(16,185,129,0.1); border: 1px solid #10b981; border-radius: 12px; padding: 14px 20px; text-align: center; margin-top: 10px; magin-bottom: 20px;">
            <span style="font-size: 1.05rem; color: #10b981; font-weight: 700;">
            Modelo Cinético Más Probable: 
            <span style="color: #ffffff; text-decoration: underline;">{mejor_orden}</span> 
            con un ajuste de R² = 
            <span style="color: #ffffff;">{mejor_r2:.4f}</span>
        </span>
    </div>
    """, unsafe_allow_html=True)
    
        st.header("3. Determinación de Parámetros Cinéticos")

        A0 = A[0]  # Concentración inicial [A]0

        if mejor_orden == "Orden Cero (0)":
            k_val = abs(res_0.slope)
            unidades_k = "M/min"
            t50 = (0.50 * A0) / k_val  
            t90 = (0.10 * A0) / k_val
            t95 = (0.05 * A0) / k_val
            t98 = (0.02 * A0) / k_val

        elif mejor_orden == "Orden Uno (1)":
            k_val = abs(res_1.slope)
            unidades_k = "min⁻¹"
            t50 = np.log(2) / k_val  
            t90 = -np.log(0.90) / k_val  
            t95 = -np.log(0.95) / k_val  
            t98 = -np.log(0.98) / k_val  

        elif mejor_orden == "Orden Dos (2)":
            k_val = abs(res_2.slope)
            unidades_k = "M⁻¹·min⁻¹"
            t50 = 1.0 / (k_val * A0)  
            t90 = 1.0 / (9.0 * k_val * A0)  
            t95 = 1.0 / (19.0 * k_val * A0)  
            t98 = 1.0 / (49.0 * k_val * A0)  

        st.subheader("⏱ Constante Cinética (k) y Tiempos de Vida Útil")
        st.info(f" **Constante Cinética (k):** {k_val:.6f} {unidades_k}")

        # 1. TARJETA DESTACADA (HERO CARD) PARA t90 (Vida Útil Farmacéutica) 
        st.markdown(f""" 
        <div style="background: linear-gradient(135deg, #064e3b 0%, #022c22 100%); border: 2px solid #10b981; border-radius: 16px; padding: 22px; text-align: center; box-shadow: 0 8px 24px rgba(16, 185, 129, 0.25); margin-bottom: 20px">
        <span style="backgroun-color: #10b981; color: ##35b596; font-size: 0.75rem; font-weight: 900; padding: 4px 14px; border-radius: 20px; text-transform: uppercase; letter-spacing: 1px;">
            ⭐ Estándar Farmacéutico (ICH / OMS) 
        </span> 
        <div style="font-size: 1.1rem; color: #a7f3d0; font-weight: 700; margin-top: 10px;">
            t₉₀ — Vida Útil Comercial (10% Degradación) 
        </div> 
        <div style="font-size: 2.6rem; color: #ffffff; font-weight: 800; margin: 6px 0; text-shadow: 0 2px 10px rgba(0,0,0,0.3);">
            {t90:.2f} <span style="font-size: 1.2rem; font-weight: 500; color: #a7f3d0;">min</span>
            </div>
            <div style="font-size: 0.85rem; color: #6ee7b7; font-weight: 500;"> 
                Tiempo estimado para conservar el 90% de la potencia activa del principio farmacéutico. 
                </div>
            </div> 
            """, unsafe_allow_html=True)
        
        # 2. FILA SECUNDARIA DE TIEMPOS (t50, t95, t98) CON BORDES DE COLOR 
        col_sec1, col_sec2, col_sec3 = st.columns(3)

        with col_sec1:
            st.markdown(f"""
            <div style="background: #1e293b; border-top: 4px solid #3b82f6; border-radius: 12px; padding: 14px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.2);">
                <div style="font-size: 0.8rem; color: #94a3b8; font-weight: 700; text-transform: uppercase;">t₅₀ — Vida Media</div>
                <div style="font-size: 1.5rem; color: #60a5fa; font-weight: 800; margin: 4px 0;">{t50:.2f} min</div>
                <div style="font-size: 0.75rem; color: #64748b;">50% de principio activo remanente</div>
            </div>
            """, unsafe_allow_html=True)

        with col_sec2:
            st.markdown(f"""
            <div style="background: #1e293b; border-top: 4px solid #a855f7; border-radius: 12px; padding: 14px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.2);">
                <div style="font-size: 0.8rem; color: #94a3b8; font-weight: 700; text-transform: uppercase;">t₉₅ — Estabilidad Alta</div>
                <div style="font-size: 1.5rem; color: #c084fc; font-weight: 800; margin: 4px 0;">{t95:.2f} min</div>
                <div style="font-size: 0.75rem; color: #64748b;">5% de degradación tolerada</div>
            </div>
            """, unsafe_allow_html=True)

        with col_sec3:
            st.markdown(f"""
            <div style="background: #1e293b; border-top: 4px solid #f97316; border-radius: 12px; padding: 14px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.2);">
                <div style="font-size: 0.8rem; color: #94a3b8; font-weight: 700; text-transform: uppercase;">t₉₈ — Límite Estricto</div>
                <div style="font-size: 1.5rem; color: #fb923c; font-weight: 800; margin: 4px 0;">{t98:.2f} min</div>
                <div style="font-size: 0.75rem; color: #64748b;">2% de degradación tolerada</div>
            </div>
            """, unsafe_allow_html=True)

        st.divider()
    
# ========================================== 
# 3. MÓDULO DE ARRHENIUS 
# ========================================== 
with tab_arrhenius: 
    st.header("4. Módulo de Arrhenius: Efecto de la Temperatura") 
    st.write("Ingresa las constantes cinéticas ($k$) obtenidas experimentalmente a distintas temperaturas ($T$):") 

    # Prioridad: 1. Hoja 2 del Excel subido > 2. Ejemplo > 3. Tabla limpia 
    if df_arr_from_file is not None: 
        df_arr_init = df_arr_from_file 
    elif cargar_ejemplo: 
        df_arr_init = pd.DataFrame({ 
            "Temperatura (°C)": [25.0, 35.0, 45.0, 55.0], 
            "Constante k": [0.0012, 0.0031, 0.0075, 0.0172] 
        }) 
    else: 
        df_arr_init = pd.DataFrame({ 
            "Temperatura (°C)": [None, None, None, None], 
            "Constante k": [None, None, None, None] 
            }) 
        
    df_arr_editor = st.data_editor(df_arr_init, num_rows="dynamic", key="tabla\_arrhenius")
    temp_c_arr = pd.to_numeric(df_arr_editor.iloc[:, 0], errors='coerce').values 
    k_exp_arr = pd.to_numeric(df_arr_editor.iloc[:, 1], errors='coerce').values 
    mask_arr = ~np.isnan(temp_c_arr) & ~np.isnan(k_exp_arr) & (k_exp_arr > 0) 
    
    temp_c_valid = temp_c_arr[mask_arr] 
    k_exp_valid = k_exp_arr[mask_arr] 
    
    if len(temp_c_valid) >= 2: 
        T_kelvin = temp_c_valid + 273.15 
        inv_T = 1.0 / T_kelvin 
        ln_k = np.log(k_exp_valid) 
       
        res_arr = linregress(inv_T, ln_k) 
        r2_arr = res_arr.rvalue**2 
        R_gas = 8.314472 # J / (mol·K) 
        Ea_J = -res_arr.slope * R_gas 
        Ea_kJ = Ea_J / 1000.0 
        A_factor = np.exp(res_arr.intercept) 
        
        signo_arr = "+" if res_arr.intercept >= 0 else "" 
        ecuacion_arr = f"ln(k) = {res_arr.slope:.2f}·(1/T) {signo_arr} {res_arr.intercept:.4f}"

        st.divider() 
        st.subheader("🔥 Parámetros Termodinámicos de Arrhenius")   

        # 1. TARJETA HÉROE PARA ENERGÍA DE ACTIVACIÓN (Ea) 
        st.markdown(f""" 
        <div style="background-color: linear-gradient(135deg, #7c2d12 0%, #451a03 100%); border: 2px solid #f97316; border-radius: 16px; padding: 22px; text-align: center; box-shadow: 0 8px 24px rgba(249, 115, 22, 0.25); margin-bottom: 20px;"> 
            <span style="background-color: #f97316; color: #451a03; font-size: 0.75rem; font_weight: 800; padding: 4px 14px; border-radius: 20px; text-transform: uppercase; letter-spacing: 1px;">
                🔥 Barrera Energética (Ea) 
            </span> 
            <div style="font.size: 1.1rem; color: #ffedd5; fon-weight: 600, margin-tp: 10px;">
                Energía de Activación del Proceso 
            </div> 
            <div style="font-size: 2.6rem; color: #ffffff; font-weight: 800; margin: 6px 0; text-shadow: 0 2px 10px rgba (0,0,0,0.3);"> 
                {Ea_kJ:.2f} <span style="font-size: 1.2rem; font-weight: 500; color: #ffedd5;">kJ/mol</span> 
            </div> 
            <div style="font-size: 0.85rem; color: #fed7aa; font-weigth: 500;"> 
                Equivalente a <b>{Ea_J:.2f} J/mol</b> — Determina la susceptibilidad del fármaco al incremento de temperatura. 
            </div> 
        </div> 
        """, unsafe_allow_html=True)

        # 2. TARJETAS SECUNDARIAS (A y R²) 
        col_arr1, col_arr2 = st.columns(2) 
       
        with col_arr1: 
            st.markdown(f"""
            <div style="background: #1e293b; border-top: 4px solid #38bdf8; border-radius: 12px; padding: 14px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.2);">
                <div style="font-size: 0.8rem; color: #94a3b8; font-weight: 700; text-transform: uppercase;">Factor Preexponencial (A)</div>
                <div style="font-size: 1.5rem; color: #38bdf8; font-weight: 800; margin: 4px 0;">{A_factor:.4e}</div>
                <div style="font-size: 0.75rem; color: #64748b;">Frecuencia de colisiones molecularon efectivas</div>
            </div>
            """, unsafe_allow_html=True)

        with col_arr2: 
            st.markdown(f"""
            <div style="background: #1e293b; border-top: 4px solid #4ade80; border-radius: 12px; padding: 14px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.2);">
                <div style="font-size: 0.8rem; color: #94a3b8; font-weight: 700; text-transform: uppercase;">Ajuste Lineal de Arrhenius (R²)</div>
                <div style="font-size: 1.5rem; color: #4ade80; font-weight: 800; margin: 4px 0;">{r2_arr:.4f}</div>
                <div style="font-size: 0.75rem; color: #64748b;">Coeficiente de determinación de la regresión</div>
            </div>
            """, unsafe_allow_html=True)

        # 3. DETALLES DE LA REGRESIÓN DE ARRHENIUS
        st.markdown(f"""      
        <div style="background: #0f172a; border: 1px solid #1e293b; border-radius: 12px; padding: 16px; margin-top: 18px; margin-bottom: 20px;">
            <div style="font-size: 0.95rem; color: #38bdf8; font-weight: 700; margin-bottom: 8px;">📐 Ecuación Linealizada de Arrhenius</div>
            <div style="font-family: monospace; font-size: 1.1rem; color: #f8fafc; background: #1e293b; padding: 10px; border-radius: 8px; border-left: 4px solid #f97316; margin-bottom: 10px;">
                {ecuacion_arr}
            </div>
            <div style="font-size: 0.85rem; color: #cbd5e1; line-height: 1.6;">
                • <b>Pendiente (m = -Ea/R):</b> <code style="color:#f97316">{res_arr.slope:.4f}</code><br> 
                • <b>Intercepto (b = ln A):</b> <code style="color:#38bdf8">{res_arr.intercept:.4f}</code>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 4. TABLA EXPANDIBLE DE DATOS TRANSFORMADOS (1/T y Ln k)
        df_transformado = pd.DataFrame({
            "Temp (°C)": temp_c_valid,
            "Temp (K)": T_kelvin,
            "1/T (K⁻¹)": inv_T,
            "Constante k": k_exp_valid,
            "ln(k)": ln_k
        })

        with st.expander("🗒️ Ver Tabla de Datos Transformados (1/T y ln(k))"):
            st.dataframe(df_transformado.style.format({
                "Temp (K)": "{:.2f}",
                "1/T (K⁻¹)": "{:.6f}",
                "Constante k": "{:.6e}",
                "ln(k)": "{:.4f}"
            }), width='stretch')

        # 5. GRÁFICO MEJORADO DE ARRHENIUS
        fig_arr = go.Figure()

        # Puntos Experimentales
        fig_arr.add_trace(go.Scatter(
            x=inv_T,
            y=ln_k,
            mode='markers',
            name='Datos Experimentales',
            marker=dict(size=12, color='#f97316', line=dict(width=2, color='#ffffff')),
            hovertemplate="<b>1/T:</b> %{x:.6f} K⁻¹<br><b>ln(k):</b> %{y:.4f}<extra></extra>"
        ))

        # Línea de ajuste
        x_línea_arr = np.linspace(inv_T.min(), inv_T.max(), 100)
        y_línea_arr = res_arr.slope * x_línea_arr + res_arr.intercept
        fig_arr.add_trace(go.Scatter(
            x=x_línea_arr,
            y=y_línea_arr,
            mode='lines',
            name=f'Ajuste Arrhenius (R²={r2_arr:.4f})',
            line=dict(color='#38bdf8', width=3, dash='dash')
        ))

        fig_arr.update_layout(
            title="🔥 Gráfico de Arrhenius: ln(k) vs 1/T",
            xaxis_title="1/T (K⁻¹)",
            yaxis_title="ln (k)",
            template="plotly_dark",
            legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99)
        )

        st.plotly_chart(fig_arr, width='stretch')
    else:
        st.warning("⚠️ Ingresa al menos 2 pares válidos de Temperatura (°C) y constante k (>0) para calcular la ecuación de Arrhenius.")

# ==========================================
# 4. PREDICCIÓN DE ESTABILIDAD
# ==========================================
with tab_prediccion:
    st.header("4. Predicción de Estabilidad Farmacéutica ")

    if (len(t) >= 3) and (len(temp_c_valid) >= 2):
        st.write("Selecciona o ingresa la temperatura de almacenamiento esperada para predecir el comportamiento de estabilidad")

        # Selector de temperatura estabilizado
        col_input, col_space = st.columns([1, 2])
        with col_input:
            temp_pred_c = st.number_input(
                "Temperatura a evaluar (°C):",
                value=25.0,
                step=1.0,
                key="temp_pred_user"
            )

        # Predicción de k por Arrhenius
        T_pred_k = temp_pred_c + 273.15
        inv_T_pred = 1.0 / T_pred_k
        ln_k_pred = res_arr.slope * inv_T_pred + res_arr.intercept
        k_pred = np.exp(ln_k_pred)

        # Tiempos predichos según el orden cinético ganador
        if "Cero" in mejor_orden:
            t50_pred = (0.50 * A0) / k_pred
            t90_pred = (0.10 * A0) / k_pred
            t95_pred = (0.05 * A0) / k_pred
            t98_pred = (0.10 * A0) / k_pred
        elif "Uno" in mejor_orden:
            t50_pred = np.log(2) / k_pred
            t90_pred = -np.log(0.90) / k_pred
            t95_pred = -np.log(0.95) / k_pred
            t98_pred = -np.log(0.98) / k_pred
        else: 
            t50_pred = 1.0 / (k_pred * A0)
            t90_pred = 1.0 / (9.0 * k_pred * A0)
            t95_pred = 1.0 / (19.0 * k_pred * A0)
            t98_pred = 1.0 / (49.0 * k_pred * A0)

        st.divider()
        st.subheader(f" Comportamiento Cinético Predicho a {temp_pred_c:.1f} °C")
        st.info(f" **Constante Cinética Predicha (k):** `{k_pred:.6e}`{unidades_k}")

        # 1. TARJETA HÉROE PARA t90 PREDICHO
        st.markdown(f""" 
        <div style="background: linear-gradient(135deg, #1e1b4b 0%, #0f172a 100%); border: 2px solid #6366f1; border-radius: 16px; padding: 22px; text-align: center; box-shadow: 0 8px 24px rgba(99, 102, 241, 0.25); margin-bottom: 20px;"> 
            <span style="background-color: #6366f1; color: #ffffff; font-size: 0.75rem; font_weight: 800; padding: 4px 14px; border-radius: 20px; text-transform: uppercase; letter-spacing: 1px;">
                Vida Útil Predicha (t₉₀)
            </span> 
            <div style="font.size: 1.1rem; color: #c7d2fe; fon-weight: 600, margin-tp: 10px;">
                Vida Útil Estimada a {temp_pred_c:.1f} °C (10% Degradación)
            </div> 
            <div style="font-size: 2.6rem; color: #ffffff; font-weight: 800; margin: 6px 0; text-shadow: 0 2px 10px rgba (0,0,0,0.3);"> 
                {t90_pred:.2f} <span style="font-size: 1.2rem; font-weight: 500; color: #c7d2fe;">min</span> 
            </div> 
            <div style="font-size: 0.85rem; color: #a5b4fc; font-weigth: 500;"> 
                Tiempo proyectado antes de perder el 10% de la potencia activa según el modelo de Arrhenius.    
            </div> 
        </div> 
        """, unsafe_allow_html=True)

        # 2. TARJETAS SECUNDARIAS PREDICHAS (t50,t95,t98)
        col_p1, col_p2, col_p3 = st.columns(3) 
       
        with col_p1: 
            st.markdown(f"""
            <div style="background: #1e293b; border-top: 4px solid #3b82f6; border-radius: 12px; padding: 14px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.2);">
                <div style="font-size: 0.8rem; color: #94a3b8; font-weight: 700; text-transform: uppercase;">t₅₀ Predicho - Vida Media</div>
                <div style="font-size: 1.5rem; color: #68a5fa; font-weight: 800; margin: 4px 0;">{t50_pred:.2f} min</div>
                <div style="font-size: 0.75rem; color: #64748b;">50% de degradación estimada</div>
            </div>
            """, unsafe_allow_html=True)

        with col_p2: 
            st.markdown(f"""
            <div style="background: #1e293b; border-top: 4px solid #4ade80; border-radius: 12px; padding: 14px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.2);">
                <div style="font-size: 0.8rem; color: #94a3b8; font-weight: 700; text-transform: uppercase;">t₉₅ Predicho - Estabilidad Alta</div>
                <div style="font-size: 1.5rem; color: #c004fc; font-weight: 800; margin: 4px 0;">{t95_pred:.2f}</div>
                <div style="font-size: 0.75rem; color: #64748b;">5% de degradación tolerada</div>
            </div>
            """, unsafe_allow_html=True)        

        with col_p3: 
            st.markdown(f"""
            <div style="background: #1e293b; border-top: 4px solid #4ade80; border-radius: 12px; padding: 14px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.2);">
                <div style="font-size: 0.8rem; color: #94a3b8; font-weight: 700; text-transform: uppercase;">t₉₈ Predicho - Límite Estrcito</div>
                <div style="font-size: 1.5rem; color: #fb923c; font-weight: 800; margin: 4px 0;">{t98_pred:.2f}</div>
                <div style="font-size: 0.75rem; color: #64748b;">2% de degradación tolerada</div>
            </div>
            """, unsafe_allow_html=True)   

        # --- DIAGNÓSTICO AUTOMÁTICO DE LA IA MULTIRRANGO ___
        st.divider()
        st.subheader("Conclusión Automática de Estabilidad Farmacéutica")

        # Clasificación de sensibilidad térmica según Ea
        if Ea_kJ > 75.0: 
            Sensibilidad = "Alta ⚠️ (Altamente termolábil; muy susceptible a cambios térmicos por lo que requiere control estricto de temperatura)" 
        elif Ea_kJ >= 40.0: 
            Sensibilidad = "Moderada 🟡 (Sensibilidad térmica estándar)" 
        else: 
            Sensibilidad = "Baja 🟢 (Termoestable; poco influenciada por la temperatura)"

        # Diagnóstico por rango climático (Estándares ICH / OMS)
        if temp_pred_c < 0.0: 
            zona_clima = "Condición de Congelación (< 0 °C)" 
            recomendacion = "nivel de disminución sustancial de la velocidad de degradación. Se debe verificar que la formulación soporte ciclos de congelación-descongelación sin precipitación del activo ni separación de fases." 
            badge_color = "#38bdf8"
        elif 2.0 <= temp_pred_c <= 8.0: 
            zona_clima = "Condición de Refrigeración (2 °C - 8 °C)" 
            recomendacion = "estado de conservación Óptima. La disminución de energía térmica frena significativamente la constante k, desacelerando la descomposición del activo."
            badge_color = "#00D2FF"
        elif 15.0 <= temp_pred_c <= 25.0: 
            zona_clima = "Condición Ambiente Estándar (Zona ICH I/II - 15 °C a 25 °C)" 
            recomendacion = "comportamiento estable dentro de los parámetros comerciales previstos para almacenamiento en estantería convencionales."
            badge_color = "#10b981"
        elif 30.0 <= temp_pred_c <= 39.0: 
            zona_clima = "Condición Tropical / Cálida (Zona ICH IV - 30 °C)" 
            recomendacion = "nivel de aceleración moderada en la cinética de degradación. Se sugiere empaque primario con alta barrera a la humedad e indicación 'Mantener por debajo de 30 °C'."
            badge_color = "#f59e0b"
        elif 40.0 <= temp_pred_c <= 59.0: 
            zona_clima = "Condición de Estrés Térmico Acelerado (40 °C)" 
            recomendacion = "nivel de degradación acelerada crítica (Condición ICH Q1A). Debe monitorearse la aparición de productos de degradación secundarios y pérdida de potencia."
            badge_color = "#f97316"
        else: 
            zona_clima = "Condición de Degradación Extrema (≥ 60 °C)" 
            recomendacion = "riesgo alto de desnaturalización, termólisis o descomposición inmediata. Evitar cualquier exposición a esta temperatura."
            badge_color = "#ef4444"
        
        # Factor de aceleración respecto a 25°C 
        T_25_k = 25.0 + 273.15 
        ln_k_25 = res_arr.slope * (1.0 / T_25_k) + res_arr.intercept 
        k_25 = np.exp(ln_k_25) 
        ratio_k = k_pred / k_25

        if ratio_k > 1.05: 
            efecto_k = f"La velocidad de degradación se incrementa {ratio_k:.2f} veces con respecto a los 25 °C." 
        elif ratio_k > 0.95: 
            efecto_k = f"La velocidad de degradación se reduce {(1.0/ratio_k):.2f} vez/veces más en comparación con 25 °C." 
        else: 
            efecto_k = "La velocidad de reacción es equivalente a la condición estándar de 25 °C."        

        diagnostico_text = f""" 
        El proceso de degradación del principio activo sigue de manera rigurosa un modelo de **{mejor_orden}** (ajuste de $R^2 = {mejor_r2:.4f}$) con una energía de activación de **{Ea_kJ:.2f} kJ/mol**, lo que evidencia una sensibilidad térmica  **{Sensibilidad}**. A la temperatura evaluada de **{temp_pred_c:.1f} °C**, se determina una constante cinética de **{k_pred:.4e} {unidades_k}**, indicando que {efecto_k}. En consecuencia, se proyecta una vida útil comercial de **{t90_pred:.2f} minutos**, concluyendo que a esta condición de almacenamiento ({zona_clima}) se presenta un {recomendacion}
"""
        st.success(diagnostico_text) 

    else:
        st.warning("⚠️ Completa los datos en la **Pestaña 1** (Cinética) y la **Pestaña 3** (Arrhenius) para habilitar las predicciones del asistente de IA.")
        