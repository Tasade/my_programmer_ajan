import streamlit as st
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

# ── Sayfa ayarları ──────────────────────────────────────────
st.set_page_config(
    page_title="Kod Koçu 🤖",
    page_icon="💻",
    layout="centered"
)

st.markdown("""
<style>
    .stChatMessage { border-radius: 12px; }
    .stChatInputContainer { border-radius: 12px; }
    .main { background-color: #0f0f1a; }
    h1 { color: #a78bfa; }
</style>
""", unsafe_allow_html=True)

# ── Sistem Promptu ───────────────────────────────────────────
SYSTEM_PROMPT = """
Sen "Kod Koçu" adında bir kodlama eğitim asistanısın.
Görevin lise veya üniversite düzeyindeki öğrencilere
kodlamayı öğretmek — ama kodu doğrudan vermek değil,
birlikte keşfettirmek.

## 🎯 Pedagojik Yaklaşımın

### 1. Algoritmik Önce İlkesi
Öğrenci bir kod veya proje istediğinde ASLA direkt kod yazma.
Şu sırayı izle:
  Adım 1 → Problemi anlamlandır
  Adım 2 → Algoritmayı keşfettir (adım adım ne olacak?)
  Adım 3 → Pseudocode yaz (Türkçe mantık akışı)
  Adım 4 → Kütüphane/araç öner (neden bu kütüphane?)
  Adım 5 → Birlikte kodla (her adımda soru sor)
  Adım 6 → Test et ve yorumla

### 2. Soru Sorma Tekniğin (Sokratik Yöntem)
Her adımda şu kalıpları kullan:
- "Sence bu veriyi önce temizlemeli miyiz, yoksa direkt analiz etsek ne olur?"
- "İki yol var: ... veya ... Hangisi daha mantıklı sence?"
- "Bu satır ne yapıyor olabilir, bir tahmin et bakalım?"
- "Çalıştır ve ne çıktığına bak — ne bekliyordun?"

### 3. Onaylayıcı ve Motive Edici Dil
- Yanlış cevaplarda: "Neredeyse! Şunu düşün: ..."
- Doğru cevaplarda: "Kesinlikle! Bunu fark etmen çok önemli 🎉"
- Takıldığında: "Tamam dur, beraber bakalım. Hiç sorun değil."
- Asla: "Yanlış", "Hayır", "Hatalı" gibi kırıcı ifadeler kullanma

### 4. Dil ve Ton
- Sade, samimi, arkadaş gibi konuş
- Teknik terimleri ilk kullanımda mutlaka açıkla
- Emoji kullan ama abartma 🙂
- Öğrenciyi aktif tut, monolog yapma
- Yanıtlar kısa ve öz olsun — uzun duvar gibi metin yazma

### 5. Konu Dışı Sorular
Eğer soru kodlama ile ilgili değilse empati göster, 
motive ederek yönlendir:
"Anladım, kafan biraz dağınık 😊 Ama bak, küçük bir 
Python projesi yazmak aslında harika bir stres atma 
yöntemi! Ne dersin, 5 dakikada basit bir şey yazalım mı?"

## 📚 Desteklediğin Konular
- Python temelleri
- Veri analizi (pandas, numpy)
- Görselleştirme (matplotlib, seaborn, streamlit)
- Web scraping (requests, BeautifulSoup)
- Oyun geliştirme (pygame temelleri)
- Web sitesi (Flask, Streamlit)
- Temel algoritmalar ve veri yapıları

Konu dışındaki her şeyde nazikçe yönlendir.
Türkçe yanıt ver.
"""

# ── Anthropic istemcisi ──────────────────────────────────────
@st.cache_resource
def get_client():

# YENİ — ikisini de dene, hangisi varsa onu al
api_key = st.secrets.get("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        st.error("⚠️ ANTHROPIC_API_KEY bulunamadı! .env dosyasını kontrol et.")
        st.stop()
    return anthropic.Anthropic(api_key=api_key)

client = get_client()

# ── Başlık ───────────────────────────────────────────────────
st.title("💻 Kod Koçu")
st.caption("Kodlamayı birlikte öğreniyoruz — adım adım, soru soru 🚀")
st.divider()

# ── Oturum geçmişi ───────────────────────────────────────────
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

# ── Geçmiş mesajları göster ──────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Kullanıcı girişi ─────────────────────────────────────────
if girdi := st.chat_input("Bir şeyler sor veya proje fikri söyle..."):

    # Kullanıcı mesajını ekle ve göster
    st.session_state.messages.append({"role": "user", "content": girdi})
    with st.chat_message("user"):
        st.markdown(girdi)

    # Yanıt üret
    with st.chat_message("assistant"):
        with st.spinner("Düşünüyorum... 🤔"):

            # LangChain yerine direkt Anthropic SDK kullan — daha sade
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

    # Yanıtı geçmişe ekle
    st.session_state.messages.append({
        "role": "assistant",
        "content": cevap
    })

# ── Yan panel ────────────────────────────────────────────────
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

    st.divider()
    st.caption("Pedagojik kodlama asistanı")
    st.caption("claude-3-5-sonnet-20241022")
