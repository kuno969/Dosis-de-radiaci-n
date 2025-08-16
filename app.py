import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# Configuración de la página
# -----------------------------
st.set_page_config(
    page_title="Radiación vs Distancia - Angiógrafo",
    page_icon="🩻",
    layout="centered"
)

st.title("🩻 Radiación ionizante vs Distancia (Angiógrafo)")
st.write(
    "Esta herramienta educativa estima el nivel de radiación en función de la distancia, "
    "usando la **ley del inverso del cuadrado**. El modelo asume una fuente puntual y "
    "condiciones simplificadas. Para uso educativo, no clínico."
)

st.markdown("---")

# -----------------------------
# Parámetros del modelo
# -----------------------------
st.subheader("Parámetros del modelo")

col1, col2 = st.columns(2)

with col1:
    dose_1m = st.number_input(
        "Dosis de referencia a 1 m (μSv/h)",
        min_value=0.0, value=50.0, step=1.0,
        help="Tasa de dosis equivalente a 1 metro de la fuente (valor de referencia educativo)."
    )
    r0 = st.number_input(
        "Distancia de referencia r₀ (m)",
        min_value=0.1, value=1.0, step=0.1,
        help="Distancia a la que se definió la dosis de referencia (por defecto 1 m)."
    )

with col2:
    att_factor = st.slider(
        "Factor de atenuación (0–1)",
        min_value=0.0, max_value=1.0, value=1.0, step=0.01,
        help="Factor global por blindaje/atenuación (1 = sin atenuación; 0.5 ≈ 50% reducción)."
    )
    fps_factor = st.slider(
        "Factor operativo (tiempo/cuadros) (0.5–2.0)",
        min_value=0.5, max_value=2.0, value=1.0, step=0.05,
        help="Ajuste simple por configuración (p. ej. más tiempo/frames → mayor tasa)."
    )

st.caption(
    "Modelo: **D(d) = D(1m) · (r₀/d)² · factor_atenuación · factor_operativo**. "
    "No sustituye mediciones con dosímetros ni normativa local."
)

st.markdown("---")

# -----------------------------
# Control de distancia con botón
# -----------------------------
st.subheader("Distancia de evaluación")

# Estado para la distancia "aplicada"
if "dist_aplicada" not in st.session_state:
    st.session_state.dist_aplicada = 1.0

dist_input = st.number_input(
    "Ingresa la distancia (m)",
    min_value=0.1, value=st.session_state.dist_aplicada, step=0.1
)

aplicar = st.button("📏 Aplicar distancia")

if aplicar:
    st.session_state.dist_aplicada = float(dist_input)

d = st.session_state.dist_aplicada

# -----------------------------
# Cálculo de dosis
# -----------------------------
def dose_at_distance(d_m, D1m, r_ref, att=1.0, op=1.0):
    # Evitar división por cero
    d_m = np.maximum(d_m, 1e-6)
    return D1m * (r_ref / d_m)**2 * att * op

D_d = dose_at_distance(d, dose_1m, r0, att_factor, fps_factor)

st.metric(
    label=f"Tasa estimada a {d:.2f} m",
    value=f"{D_d:.2f} μSv/h",
    help="Estimación basada en el modelo simplificado indicado arriba."
)

# -----------------------------
# Curva dosis vs distancia
# -----------------------------
st.subheader("Curva: Dosis estimada vs Distancia")

dist_min = st.number_input("Distancia mínima (m)", min_value=0.1, value=0.5, step=0.1)
dist_max = st.number_input("Distancia máxima (m)", min_value=dist_min + 0.1, value=5.0, step=0.1)
num_pts = st.slider("Puntos en la curva", min_value=50, max_value=500, value=200, step=10)

d_grid = np.linspace(dist_min, dist_max, num_pts)
D_grid = dose_at_distance(d_grid, dose_1m, r0, att_factor, fps_factor)

fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(d_grid, D_grid)
ax.scatter([d], [D_d], s=50)
ax.set_xlabel("Distancia (m)")
ax.set_ylabel("Tasa de dosis (μSv/h)")
ax.set_title("Dosis estimada vs distancia (modelo inverso del cuadrado)")
ax.grid(True)

st.pyplot(fig, clear_figure=True)

# -----------------------------
# Notas y descargos
# -----------------------------
with st.expander("Notas importantes"):
    st.markdown(
        """
- **Uso educativo**: el cálculo es una *aproximación* para visualizar tendencias; no reemplaza mediciones con instrumentación (p. ej., dosímetros, cámaras de ionización).
- La radiación en angiografía depende de múltiples factores (kVp, mA, filtración, FPS, colimación, paciente, proyección, equipo).
- Considera la **normativa local** y los **Niveles de Referencia Diagnóstica (DRL)** de tu país/institución.
        """
    )

st.markdown("---")
st.info(
    "Sugerencia: registra mediciones reales (μSv/h) a varias distancias con tu servicio de física médica "
    "y compara con esta curva para ajustar el factor operativo/atenuación."
)
