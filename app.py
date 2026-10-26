import time
import unicodedata
import streamlit as st
from google import genai

# ===== MONTURAS (inicio) =====
# Dibujos sencillos de cada tipo de montura, hechos con SVG (sin fotos con derechos).
# Cada lente se dibuja a la izquierda y la app la refleja para hacer la derecha.
MONTURAS = {
    "redonda": {
        "nombre": "Redonda",
        "descripcion": "Círculos perfectos. Suavizan las caras cuadradas.",
        "lente": '<circle cx="55" cy="40" r="32"/>',
        "puente": (87, 34),
    },
    "ovalada": {
        "nombre": "Ovalada",
        "descripcion": "Suave y discreta. Va bien con casi todo.",
        "lente": '<ellipse cx="55" cy="40" rx="36" ry="24"/>',
        "puente": (91, 36),
    },
    "cuadrada": {
        "nombre": "Cuadrada",
        "descripcion": "Líneas rectas y carácter. Ideal para caras redondas.",
        "lente": '<rect x="22" y="10" width="66" height="60" rx="8"/>',
        "puente": (88, 30),
    },
    "rectangular": {
        "nombre": "Rectangular",
        "descripcion": "Clásica y profesional. Alarga las caras redondas.",
        "lente": '<rect x="15" y="22" width="76" height="38" rx="6"/>',
        "puente": (91, 34),
    },
    "aviador": {
        "nombre": "Aviador",
        "descripcion": "Forma de gota. La reina de las gafas de sol.",
        "lente": '<path d="M20,18 L90,18 Q95,18 92,32 Q86,68 56,70 Q22,70 18,38 Q16,18 20,18 Z"/>',
        "puente": (91, 24),
    },
    "cat-eye": {
        "nombre": "Ojo de gato",
        "descripcion": "Esquinas hacia arriba. Glamour y actitud.",
        "lente": '<path d="M10,14 Q40,20 88,26 Q95,28 92,42 Q88,64 58,66 Q28,66 20,46 Q14,30 10,14 Z"/>',
        "puente": (92, 34),
    },
    "hexagonal": {
        "nombre": "Hexagonal",
        "descripcion": "Geométrica y moderna. Para quien quiere destacar.",
        "lente": '<polygon points="87,40 71,68 39,68 23,40 39,12 71,12"/>',
        "puente": (87, 38),
    },
    "browline": {
        "nombre": "Ceja marcada (browline)",
        "descripcion": "Parte de arriba gruesa, estilo retro de los años 50.",
        "lente": (
            '<rect x="20" y="14" width="70" height="52" rx="14" stroke-width="3"/>'
            '<path d="M20,24 Q20,14 32,14 L78,14 Q90,14 90,24" fill="none" stroke-width="11"/>'
        ),
        "puente": (90, 22),
    },
}


def dibujar_montura(tipo, color="#1f1f1f", sol=False):
    """Devuelve el dibujo SVG de una montura, del color elegido."""
    montura = MONTURAS[tipo]
    x, y = montura["puente"]
    relleno = "#2b2b2b" if sol else "#bfe0ff"
    opacidad = "0.75" if sol else "0.35"
    return (
        '<svg viewBox="0 0 200 80" width="100%" xmlns="http://www.w3.org/2000/svg">'
        f'<g fill="{relleno}" fill-opacity="{opacidad}" stroke="{color}" '
        'stroke-width="5" stroke-linejoin="round">'
        f'{montura["lente"]}'
        f'<g transform="translate(200,0) scale(-1,1)">{montura["lente"]}</g>'
        '</g>'
        f'<path d="M{x},{y} Q100,{y - 10} {200 - x},{y}" fill="none" '
        f'stroke="{color}" stroke-width="5" stroke-linecap="round"/>'
        '</svg>'
    )


def sin_tildes(texto):
    """Quita las tildes para comparar palabras sin problemas."""
    return "".join(
        letra for letra in unicodedata.normalize("NFD", texto)
        if unicodedata.category(letra) != "Mn"
    )


def leer_tipos(texto):
    """Busca la línea 'TIPOS: ...' que escribe la IA.
    Devuelve el texto sin esa línea y la lista de tipos de montura (máx. 3)."""
    tipos = []
    lineas = []
    for linea in texto.splitlines():
        limpia = sin_tildes(linea).replace("*", "").replace("`", "").strip().lower()
        if limpia.startswith("tipos:"):
            for trozo in limpia[6:].split(","):
                trozo = trozo.strip().strip(".").replace(" ", "-")
                trozo = trozo.replace("ojo-de-gato", "cat-eye")
                if trozo in MONTURAS and trozo not in tipos:
                    tipos.append(trozo)
        else:
            lineas.append(linea)
    return "\n".join(lineas).strip(), tipos[:3]
# ===== MONTURAS (fin) =====


# ---------- Configuración de la página ----------
st.set_page_config(page_title="¿Qué gafas van contigo?", page_icon="🕶️")
st.title("🕶️ ¿Qué gafas van contigo?")
st.write(
    "Responde 6 preguntas rápidas y descubre tu **personalidad de gafas** "
    "y qué monturas te recomiendan en tu óptica. ¡Sin datos personales!"
)

# Modelos de Gemini (capa gratuita). Prueba el primero; si está
# saturado o falla, pasa al siguiente de la lista.
MODELOS = ["gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.5-flash-lite"]

# Color de los dibujos según la respuesta a la pregunta 4
COLORES = {
    "⚫ Nada": "#1f1f1f",
    "🤎 Poquito": "#8a5a2b",
    "🟢 Algo": "#2e8b57",
    "🌈 ¡Todo!": "#e0358a",
}

# ---------- Las preguntas del test ----------
cara = st.radio(
    "1. ¿Qué forma tiene tu cara?",
    ["🔵 Redonda", "🟦 Cuadrada", "🥚 Ovalada", "💎 Corazón / triangular", "🤷 Ni idea"],
)
plan = st.selectbox(
    "2. Tu plan perfecto de sábado es…",
    ["🎨 Museo y café de especialidad", "🏔️ Monte o playa", "🎉 Fiesta hasta tarde",
     "🛋️ Sofá y series", "💼 Adelantar trabajo (sin juzgar)"],
)
uso = st.radio(
    "3. ¿Para qué las quieres sobre todo?",
    ["👓 Ver de cerca / leer", "🚗 Ver de lejos / conducir", "☀️ Sol", "✨ Solo por estilo"],
)
color = st.select_slider(
    "4. ¿Cuánto color te atreves a llevar?",
    options=list(COLORES.keys()),
)
estilo = st.selectbox(
    "5. Si fueras un personaje, serías…",
    ["🕵️ Detective elegante", "🎸 Estrella de rock", "🧑‍🔬 Científica genial",
     "🏄 Surfera relajada", "👑 Realeza discreta"],
)
presupuesto = st.radio(
    "6. Presupuesto aproximado",
    ["💶 Hasta 100 €", "💶💶 100–250 €", "💶💶💶 Más de 250 €"],
    horizontal=True,
)

color_montura = COLORES[color]
sol = uso == "☀️ Sol"

# ---------- Instrucciones para la IA ----------
LISTA_TIPOS = ", ".join(MONTURAS.keys())

PROMPT = f"""Eres un asesor de estilo de una óptica, divertido y cercano.
Un cliente ha respondido este test:
- Forma de cara: {cara}
- Plan de sábado: {plan}
- Uso principal: {uso}
- Color: {color}
- Personaje: {estilo}
- Presupuesto: {presupuesto}

Responde en español, con humor y emojis, pero con consejos ópticos correctos
(por ejemplo, a caras redondas suelen favorecer monturas angulosas). No menciones
marcas reales. Si la forma de cara es "Ni idea", explica en una frase cómo mirarlo
en el espejo.

Elige las 3 monturas recomendadas SOLO de esta lista de tipos: {LISTA_TIPOS}.

Devuelve exactamente estas secciones:

### 🏷️ Tu personalidad de gafas
(un nombre divertido inventado, tipo "La Intelectual Rebelde", y 2 frases)
### 👓 Monturas que te van
(los 3 tipos elegidos, con material y color, una línea cada uno)
### 🚫 Mejor evita
(1 tipo de montura y por qué, en una frase)
### 💬 Frase para decir en la óptica
(una frase que el cliente puede enseñar al óptico para pedir lo que busca)

Y como ÚLTIMA línea, sola, escribe exactamente así los 3 tipos elegidos,
con las palabras de la lista y separados por comas:
TIPOS: tipo1, tipo2, tipo3
"""

# ---------- Botón principal ----------
if st.button("✨ Descubrir mis gafas", type="primary"):
    try:
        cliente = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        with st.spinner("Consultando al oráculo de las gafas... 🔮"):
            # Si un modelo está saturado, prueba el siguiente de la lista
            for numero, modelo in enumerate(MODELOS):
                try:
                    respuesta = cliente.models.generate_content(model=modelo, contents=PROMPT)
                    break
                except Exception:
                    if numero == len(MODELOS) - 1:
                        raise
                    time.sleep(2)

        texto, tipos = leer_tipos(respuesta.text or "")
        st.balloons()
        st.markdown(texto)

        # Dibujos de las monturas recomendadas
        if tipos:
            st.subheader("🖼️ Así son tus monturas")
            columnas = st.columns(len(tipos))
            for columna, tipo in zip(columnas, tipos):
                with columna:
                    st.markdown(dibujar_montura(tipo, color_montura, sol), unsafe_allow_html=True)
                    st.markdown(f"**{MONTURAS[tipo]['nombre']}**")
                    st.caption(MONTURAS[tipo]["descripcion"])

        st.caption("👀 Recomendación orientativa. Tu óptico te asesorará según tu graduación y medidas.")
    except KeyError:
        st.error("Falta la clave de Gemini en los secretos de la app.")
    except Exception as error:
        st.error("El oráculo está descansando 😴. Espera un minuto y vuelve a intentarlo.")
        with st.expander("Detalles técnicos (para quien lo arregle)"):
            st.write(str(error))

# ---------- Catálogo (funciona aunque la IA falle) ----------
st.divider()
with st.expander("📚 Ver el catálogo de monturas"):
    st.caption("Los dibujos cambian de color según tu respuesta a la pregunta 4. 🎨")
    columnas = st.columns(2)
    for numero, tipo in enumerate(MONTURAS):
        with columnas[numero % 2]:
            st.markdown(dibujar_montura(tipo, color_montura, sol), unsafe_allow_html=True)
            st.markdown(f"**{MONTURAS[tipo]['nombre']}**")
            st.caption(MONTURAS[tipo]["descripcion"])
