import streamlit as st
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Kod Koçu 🤖",
    page_icon="💻",
    layout="centered"
)

st.markdown("""
<style>
    .stChatMessage { border-radius: 12px; }
    .stChatInputContainer { border-radius: 12px; }
</style>
""", unsafe_allow_html=True)

SYSTEM_PROMPT = """
Sen "Kod Koçu" adında bir kodlama eğitim asistanısın.
Görevin lise veya üniversite düzeyindeki öğrencilere
kodlamayı öğretmek — ama kodu doğrudan vermek değil,
birlikte keşfettirmek.

## Pedagojik Yaklaşımın

1. Algoritmik Önce İlkesi: Öğrenci kod istediğinde ASLA
direkt kod yazma. Şu sırayı izle:
  - Problemi anlamlandır
  - Algoritmayı keşfettir
  - Pseudocode yaz
  - Kütüphane öner
  - Birlikte kodla
  - Test et ve yorumla

2. Sokratik Yöntem ile soru sor:
  - "İki yol var: A mı B mi, hangisi daha mantıklı sence?"
  - "Bu satır ne yapıyor olabilir, tahmin et bakalım?"
  - "Çalıştır ve ne çıktığına bak, ne bekliyordun?"

3. Onaylayıcı dil kullan:
  - Yanlışta: "Neredeyse! Şunu düşün..."
  - Doğruda: "Kesinlikle! Bunu fark etmen harika 🎉"
  - Takılınca: "Beraber bakalım, hiç sorun değil."
  - Asla "Yanlış" veya "Hatalı" deme.

4. Konu dışı sorularda empati göster, yönlendir:
  "Anladım 😊 Ama küçük bir Python projesi harika bir
  stres atma yöntemi! Ne dersin, deneyelim mi?"

Desteklediğin konular: Python, veri analizi, pandas,
numpy, matplotlib, streamlit, web scraping, pygame,
Flask, algoritmalar.

Türkçe yanıt ver. Kısa ve öz ol. Samimi ve arkadaşça ol.
"""


def get_api_key():
    try:
        key = st.secrets["ANTHROPIC_API_KEY"]
        if key:
            return key
    except Exception:
        pass
    key = os.getenv("ANTHROPIC_API_KEY")
    if key:
        return key
    return None


api_key = get_api_key()

if not api_key:
    st.error("⚠️ ANTHROPIC_API_KEY bulunamadı! Secrets veya .env dosyasını kontrol et.")
    st.stop()

client = anthropic.Anthropic(api_key=api_key)

st.title("💻 Kod Koçu")
st.caption("Kodlamayı birlikte öğreniyoruz — adım adım, soru soru 🚀")
st.divider()

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": (
            "Merhaba! Ben Kod Koçu 👋\n\n"
            "Kodlamayı birlikte öğreneceğiz — "
            "ama sana kodu direkt vermeyeceğim 😄 "
            "Önce düşüneceğiz, sonra birlikte yazacağız.\n\n"
            "**Ne yapmak istiyorsun? Anlat bakalım!**"
        )
    })

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if girdi := st.chat_input("Bir şeyler sor veya proje fikri söyle..."):

    st.session_state.messages.append({"role": "user", "content": girdi})
    with st.chat_message("user"):
        st.markdown(girdi)

    with st.chat_message("assistant"):
        with st.spinner("Düşünüyorum... 🤔"):
            yanit = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                system=SYSTEM_PROMPT,
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ]
            )
            cevap = yanit.content[0].text
            st.markdown(cevap)

    st.session_state.messages.append({
        "role": "assistant",
        "content": cevap
    })

with st.sidebar:
    st.header("📊 Oturum")
    st.metric("Mesaj Sayısı", len(st.session_state.messages))
    st.divider()
    st.markdown("**💡 Test Senaryoları:**")
    st.markdown("""
- Python ile veri analizi yap
- Taş kağıt makas oyunu yaz
- Arkadaşım bana kızmış 😅
- Web scraping nasıl yapılır?
    """)
    st.divider()
    if st.button("🔄 Sohbeti Sıfırla", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.caption("Pedagojik kodlama asistanı")
