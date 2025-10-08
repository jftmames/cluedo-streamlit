# app.py
import streamlit as st
import random
import hashlib
import time

# Configuración inicial
st.set_page_config(
    page_title="Cluedo Online", 
    page_icon="🕵️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Datos del juego
PERSONAJES = ["Profesor Mora", "Coronel Rubio", "Señorita Carmesí", 
              "Srta. Amapola", "Doctor Orquídea", "Señor Azul"]

ARMAS = ["Candelabro", "Cuerda", "Puñal", "Llave Inglesa", "Pistola", "Tubería"]

HABITACIONES = ["Vestíbulo", "Salón", "Comedor", "Biblioteca", "Billar", 
                "Despacho", "Jardín de Invierno", "Salón Baile", "Cocina"]

def crear_sesion_usuario():
    """Crea un ID único de sesión para cada usuario"""
    return hashlib.md5(f"{time.time()}_{random.random()}".encode()).hexdigest()[:10]

def inicializar_juego_individual():
    """Inicializa un juego completamente individual para cada usuario"""
    
    # Obtener o crear ID de sesión del usuario
    if 'user_session_id' not in st.session_state:
        st.session_state.user_session_id = crear_sesion_usuario()
    
    session_id = st.session_state.user_session_id
    
    # Inicializar estructura para este usuario específico
    if f'juego_{session_id}' not in st.session_state:
        # Solución secreta única para este usuario
        solucion = {
            'personaje': random.choice(PERSONAJES),
            'arma': random.choice(ARMAS),
            'habitacion': random.choice(HABITACIONES)
        }
        
        # Repartir cartas restantes
        cartas_restantes = [
            p for p in PERSONAJES if p != solucion['personaje']
        ] + [
            a for a in ARMAS if a != solucion['arma']
        ] + [
            h for h in HABITACIONES if h != solucion['habitacion']
        ]
        random.shuffle(cartas_restantes)
        
        # Configuración del juego individual
        juego_data = {
            'solucion': solucion,
            'jugador': {
                'nombre': 'Detective',
                'cartas': cartas_restantes[:len(cartas_restantes)//2],
                'posicion': random.choice(HABITACIONES),
                'notas': {categoria: [] for categoria in ['personajes', 'armas', 'habitaciones']}
            },
            'ia': {
                'nombre': 'Asistente Virtual',
                'cartas': cartas_restantes[len(cartas_restantes)//2:],
                'posicion': random.choice(HABITACIONES)
            },
            'turno': 'jugador',
            'historial': [],
            'estado': "movimiento",
            'juego_activo': True,
            'resultado': None
        }
        
        st.session_state[f'juego_{session_id}'] = juego_data

def obtener_juego_actual():
    """Obtiene los datos del juego para el usuario actual"""
    session_id = st.session_state.user_session_id
    return st.session_state[f'juego_{session_id}']

def actualizar_juego_actual(juego_data):
    """Actualiza los datos del juego para el usuario actual"""
    session_id = st.session_state.user_session_id
    st.session_state[f'juego_{session_id}'] = juego_data

def hacer_sugerencia_individual(personaje, arma, habitacion, juego_data):
    """Procesa una sugerencia para el juego individual"""
    sugerencia = f"💡 **Sugerencia**: {personaje} con {arma} en {habitacion}"
    juego_data['historial'].append(sugerencia)
    
    # Verificar si la IA puede refutar
    cartas_refutacion = []
    for carta in [personaje, arma, habitacion]:
        if carta in juego_data['ia']['cartas']:
            cartas_refutacion.append(carta)
    
    if cartas_refutacion:
        carta_mostrada = random.choice(cartas_refutacion)
        juego_data['historial'].append(f"🛡️ **{juego_data['ia']['nombre']}** muestra: {carta_mostrada}")
        # Agregar a notas del jugador
        juego_data['jugador']['notas'] = actualizar_notas(
            juego_data['jugador']['notas'], carta_mostrada, True
        )
    else:
        juego_data['historial'].append("✅ **Nadie puede refutar la sugerencia**")
    
    return juego_data

def hacer_acusacion_individual(personaje, arma, habitacion, juego_data):
    """Procesa una acusación final para el juego individual"""
    solucion = juego_data['solucion']
    if (personaje == solucion['personaje'] and 
        arma == solucion['arma'] and 
        habitacion == solucion['habitacion']):
        juego_data['juego_activo'] = False
        juego_data['resultado'] = "ganador"
        return True, "🎉 **¡Correcto! Has resuelto el misterio.**"
    else:
        juego_data['juego_activo'] = False
        juego_data['resultado'] = "perdedor"
        return False, f"💀 **Incorrecto. La solución era: {solucion['personaje']} con {solucion['arma']} en {solucion['habitacion']}**"

def actualizar_notas(notas, elemento, tiene):
    """Actualiza las notas de deducción del jugador"""
    categoria = None
    if elemento in PERSONAJES:
        categoria = 'personajes'
    elif elemento in ARMAS:
        categoria = 'armas'
    elif elemento in HABITACIONES:
        categoria = 'habitaciones'
    
    if categoria and elemento not in [item[0] for item in notas[categoria]]:
        notas[categoria].append((elemento, tiene))
    
    return notas

def turno_ia(juego_data):
    """Ejecuta el turno de la IA de forma básica"""
    if juego_data['turno'] == 'ia' and juego_data['juego_activo']:
        # IA se mueve a habitación aleatoria
        habitacion_actual = juego_data['ia']['posicion']
        habitaciones_disponibles = [h for h in HABITACIONES if h != habitacion_actual]
        nueva_habitacion = random.choice(habitaciones_disponibles)
        juego_data['ia']['posicion'] = nueva_habitacion
        
        juego_data['historial'].append(f"🤖 **{juego_data['ia']['nombre']}** se mueve a **{nueva_habitacion}**")
        
        # IA hace sugerencia aleatoria (pero no puede acusar en esta versión simple)
        personaje_sug = random.choice(PERSONAJES)
        arma_sug = random.choice(ARMAS)
        
        sugerencia = f"💡 **{juego_data['ia']['nombre']}** sugiere: {personaje_sug} con {arma_sug} en {nueva_habitacion}"
        juego_data['historial'].append(sugerencia)
        
        # Verificar si jugador puede refutar
        cartas_refutacion = []
        for carta in [personaje_sug, arma_sug, nueva_habitacion]:
            if carta in juego_data['jugador']['cartas']:
                cartas_refutacion.append(carta)
        
        if cartas_refutacion:
            carta_mostrada = random.choice(cartas_refutacion)
            juego_data['historial'].append(f"🛡️ **Tú** muestras: {carta_mostrada}")
            # Actualizar notas de la IA (simulado)
            juego_data['jugador']['notas'] = actualizar_notas(
                juego_data['jugador']['notas'], carta_mostrada, True
            )
        else:
            juego_data['historial'].append("✅ **Nadie puede refutar la sugerencia de la IA**")
        
        juego_data['turno'] = 'jugador'
    
    return juego_data

def mostrar_reglas():
    """Muestra las reglas del juego en un expander"""
    with st.expander("📖 Reglas del Cluedo - Cómo jugar"):
        st.markdown("""
        ### 🎯 Objetivo
        Descubrir quién cometió el crimen, con qué arma y en qué habitación.

        ### 🔄 Turno de Juego
        1. **Moverse** a una habitación diferente
        2. **Hacer una sugerencia** con:
           - Personaje + Arma + Habitación actual
        3. **Refutación**: El oponente muestra una carta si la tiene
        4. **Turno de la IA**: Repite el proceso

        ### ⚡ Acusación Final
        - Cuando estés seguro, haz la acusación final
        - Si aciertas: ¡Ganas!
        - Si fallas: Pierdes la partida

        ### 💡 Estrategia
        - Usa las cartas que te muestran para descartar opciones
        - Lleva notas de lo que vas descubriendo
        - No hagas acusaciones tempranas
        """)

# --- INICIALIZACIÓN INDIVIDUAL ---
inicializar_juego_individual()
juego_actual = obtener_juego_actual()

# --- INTERFAZ PRINCIPAL ---
st.title("🕵️ Cluedo - Detective Online")
st.markdown("***¡Resuelve el misterio por tu cuenta!***")

# Mostrar reglas
mostrar_reglas()

# Mostrar resultado final si el juego terminó
if not juego_actual['juego_activo']:
    st.markdown("---")
    if juego_actual['resultado'] == "ganador":
        st.balloons()
        st.success("## 🎉 ¡Felicidades! Has ganado el juego.")
        st.markdown("**¡Eres un detective excepcional!**")
    else:
        st.error("## 💀 Game Over - Has perdido el juego.")
        st.markdown("**¡No te rindas! Inténtalo de nuevo.**")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Jugar de nuevo", type="primary", use_container_width=True):
            # Reiniciar solo la sesión actual
            session_id = st.session_state.user_session_id
            del st.session_state[f'juego_{session_id}']
            st.rerun()
    
    st.stop()

st.markdown("---")

# Sidebar para controles individuales
with st.sidebar:
    st.header("🎮 Controles del Juego")
    
    if st.button("🔄 Reiniciar Mi Juego", use_container_width=True):
        session_id = st.session_state.user_session_id
        del st.session_state[f'juego_{session_id}']
        st.rerun()
    
    st.markdown("---")
    st.subheader("📋 Tus Cartas")
    for carta in juego_actual['jugador']['cartas']:
        st.write(f"• {carta}")
    
    st.markdown("---")
    st.subheader("📝 Tus Notas")
    with st.expander("Ver notas de deducción"):
        for categoria, elementos in juego_actual['jugador']['notas'].items():
            if elementos:
                st.write(f"**{categoria.title()}:**")
                for elemento, tiene in elementos:
                    icono = "✅ Confirmado" if tiene else "❌ Descartado"
                    st.write(f"{icono}: {elemento}")
            else:
                st.write(f"**{categoria.title()}:** Sin información")

# Layout principal
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🔍 Tablero de Juego")
    
    # Estado actual
    st.info(f"**Turno actual**: {'🧑 Tu turno' if juego_actual['turno'] == 'jugador' else '🤖 Turno IA'} | **Tu posición**: {juego_actual['jugador']['posicion']}")
    
    # Selección de movimiento
    if juego_actual['turno'] == 'jugador' and juego_actual['estado'] == "movimiento":
        st.subheader("🚶‍♂️ Moverse a:")
        habitacion_actual = juego_actual['jugador']['posicion']
        habitaciones_disponibles = [h for h in HABITACIONES if h != habitacion_actual]
        
        cols = st.columns(3)
        for i, habitacion in enumerate(habitaciones_disponibles):
            if cols[i % 3].button(f"➡️ {habitacion}", key=f"mov_{habitacion}", use_container_width=True):
                juego_actual['jugador']['posicion'] = habitacion
                juego_actual['estado'] = "sugerencia"
                actualizar_juego_actual(juego_actual)
                st.rerun()

with col2:
    st.subheader("📝 Realizar Sugerencia")
    
    if juego_actual['turno'] == 'jugador' and juego_actual['estado'] == "sugerencia":
        with st.form("sugerencia_form"):
            st.write(f"**Estás en:** {juego_actual['jugador']['posicion']}")
            personaje_sug = st.selectbox("Personaje", PERSONAJES)
            arma_sug = st.selectbox("Arma", ARMAS)
            habitacion_sug = juego_actual['jugador']['posicion']
            
            if st.form_submit_button("🎯 Hacer Sugerencia", use_container_width=True):
                juego_actual = hacer_sugerencia_individual(
                    personaje_sug, arma_sug, habitacion_sug, juego_actual
                )
                juego_actual['turno'] = 'ia'
                juego_actual['estado'] = "movimiento"
                actualizar_juego_actual(juego_actual)
                st.rerun()

# Ejecutar turno de IA si es su turno
if juego_actual['turno'] == 'ia':
    with st.spinner("🤖 Es el turno del Asistente Virtual..."):
        time.sleep(2)  # Pequeña pausa para dar sensación de turno
        juego_actual = turno_ia(juego_actual)
        actualizar_juego_actual(juego_actual)
        st.rerun()

# Acusación final
st.markdown("---")
st.subheader("⚡ Acusación Final")
with st.expander("Hacer acusación (¡Cuidado! Si fallas, pierdes)", expanded=False):
    st.warning("⚠️ **Atención**: Solo haz la acusación cuando estés seguro. Si fallas, pierdes automáticamente.")
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        personaje_acc = st.selectbox("Personaje acusado", PERSONAJES, key="acusacion_p")
    with col_b:
        arma_acc = st.selectbox("Arma acusada", ARMAS, key="acusacion_a")
    with col_c:
        habitacion_acc = st.selectbox("Lugar del crimen", HABITACIONES, key="acusacion_h")
    
    if st.button("⚠️ HACER ACUSACIÓN FINAL", type="primary", use_container_width=True):
        correcto, mensaje = hacer_acusacion_individual(
            personaje_acc, arma_acc, habitacion_acc, juego_actual
        )
        actualizar_juego_actual(juego_actual)
        st.rerun()

# Historial del juego
st.markdown("---")
st.subheader("📜 Historial del Juego")
historial_container = st.container()
with historial_container:
    for evento in reversed(juego_actual['historial'][-8:]):
        st.write(evento)

    if not juego_actual['historial']:
        st.info("El historial aparecerá aquí. ¡Comienza moviéndote a una habitación!")

# Información de debug (opcional - comentar en producción)
# with st.expander("🔧 Debug Info (solo desarrollo)"):
#     st.write("**Solución secreta:**", juego_actual['solucion'])
#     st.write("**Cartas IA:**", juego_actual['ia']['cartas'])
#     st.write("**Estado del juego:**", juego_actual['estado'])
