import streamlit as st
from google import genai

# ---------- Configuración de la página ----------
st.set_page_config(page_title="¿Qué gafas van contigo?", page_icon="🕶️")
st.title("🕶️ ¿Qué gafas van contigo?")
st.write(
    "Responde 6 preguntas rápidas y descubre tu **personalidad de gafas** "
    "y qué monturas te recomiendan en tu óptica. ¡Sin datos personales!"
)

# Modelo de Gemini (capa gratuita). Si da error de modelo, cámbialo
# por el que aparezca en aistudio.google.com
MODELO = "gemini-3.8-flash"

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
    options=["⚫ Nada", "🤎 Poquito", "🟢 Algo", "🌈 ¡Todo!"],
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

# ---------- Instrucciones para la IA ----------
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
en el espejo. Devuelve exactamente estas secciones:

### 🏷️ Tu personalidad de gafas
(un nombre divertido inventado, tipo "La Intelectual Rebelde", y 2 frases)
### 👓 Monturas que te van
(3 tipos de montura, con forma, material y color, una línea cada una)
### 🚫 Mejor evita
(1 tipo de montura y por qué, en una frase)
### 💬 Frase para decir en la óptica
(una frase que el cliente puede enseñar al óptico para pedir lo que busca)
"""

# ---------- Botón principal ----------
if st.button("✨ Descubrir mis gafas", type="primary"):
    try:
        cliente = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        with st.spinner("Consultando al oráculo de las gafas... 🔮"):
            respuesta = cliente.models.generate_content(model=MODELO, contents=PROMPT)
        st.balloons()
        st.markdown(respuesta.text)
        st.caption("👀 Recomendación orientativa. Tu óptico te asesorará según tu graduación y medidas.")
    except KeyError:
        st.error("Falta la clave de Gemini en los secretos de la app.")
    except Exception as error:
        st.error("El oráculo está descansando 😴. Espera un minuto y vuelve a intentarlo.")
        with st.expander("Detalles técnicos (para quien lo arregle)"):
            st.write(str(error))
