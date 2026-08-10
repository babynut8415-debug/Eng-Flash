"""
영단어 카드 퀴즈 앱
- 사진/OCR 대신 영단어 목록 파일(txt/csv)을 업로드하거나 직접 입력
- 각 단어를 한국어로 번역
- 카드를 클릭하면 영단어 ↔ 한국어 뜻으로 뒤집힘
실행 방법: streamlit run app.py
"""

import re
import streamlit as st
from deep_translator import GoogleTranslator

# Windows 로컬 PC에서만 tesseract 설치 경로를 지정합니다.
# (Streamlit Cloud 등 Linux 서버에서는 packages.txt로 자동 설치되므로 이 코드가 무시됩니다.)
if platform.system() == "Windows":
    _WIN_TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if os.path.exists(_WIN_TESSERACT_PATH):
        pytesseract.pytesseract.tesseract_cmd = _WIN_TESSERACT_PATH

st.set_page_config(page_title="영단어 카드 퀴즈", page_icon="📚", layout="centered")

# ---------------------------------------------------------------------------
# 세션 상태 초기화
# ---------------------------------------------------------------------------
if "cards" not in st.session_state:
    st.session_state.cards = []  # [{"word": "apple", "meaning": "사과"}, ...]
if "idx" not in st.session_state:
    st.session_state.idx = 0
if "flipped" not in st.session_state:
    st.session_state.flipped = False


# ---------------------------------------------------------------------------
# 핵심 함수
# ---------------------------------------------------------------------------
def extract_words(image: Image.Image) -> tuple[list[str], str]:
    """사진에서 텍스트를 추출한 뒤, 중복 없는 영단어 리스트로 정리한다.
    반환값: (정리된 단어 리스트, OCR 원본 텍스트)
    """
    text = pytesseract.image_to_string(image, lang="eng")
    raw_words = re.findall(r"[A-Za-z]+(?:[-'][A-Za-z]+)*", text)

    words, seen = [], set()
    for w in raw_words:
        lw = w.lower()
        if len(lw) < 2:  # 한 글자짜리 노이즈 제거
            continue
        if lw in seen:
            continue
        seen.add(lw)
        words.append(lw)
    return words, text


@st.cache_data(show_spinner=False)
def translate_word(word: str) -> str:
    """단어 하나를 한국어로 번역한다. (결과는 캐시되어 재요청 시 재사용)"""
    try:
        return GoogleTranslator(source="en", target="ko").translate(word)
    except Exception:
        return "(번역 실패)"


def build_cards(words: list[str]) -> list[dict]:
    """단어 리스트를 받아 {word, meaning} 카드 리스트를 만든다. 진행률 표시 포함."""
    cards = []
    progress = st.progress(0, text="단어 번역 중...")
    for i, w in enumerate(words):
        meaning = translate_word(w)
        cards.append({"word": w, "meaning": meaning})
        progress.progress((i + 1) / len(words), text=f"번역 중... ({i + 1}/{len(words)})")
    progress.empty()
    return cards


def reset_quiz():
    st.session_state.idx = 0
    st.session_state.flipped = False


# ---------------------------------------------------------------------------
# 카드 스타일 (CSS)
# ---------------------------------------------------------------------------
CARD_CSS = """
<style>
.flashcard {
    width: 100%;
    min-height: 220px;
    border-radius: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 30px;
    margin: 20px 0;
    font-size: 2.2em;
    font-weight: 700;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
    word-break: break-word;
}
.card-meaning {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}
.card-word {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    color: white;
}
.card-label {
    font-size: 0.35em;
    opacity: 0.85;
    display: block;
    margin-bottom: 10px;
    font-weight: 400;
}
</style>
"""
st.markdown(CARD_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 사이드바: 업로드 & 단어 목록
# ---------------------------------------------------------------------------
st.title("📚 영단어 카드 퀴즈")
st.caption("영단어가 담긴 사진을 올리면, 단어를 추출해 한국어 뜻 카드 퀴즈를 만들어드려요.")
st.caption("🔖 코드 버전: v5 (이 문구가 안 보이면 예전 파일이 실행 중인 거예요)")

with st.sidebar:
    st.header("1. 사진 업로드")
    uploaded_file = st.file_uploader("영단어가 보이는 사진을 올려주세요", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, caption="업로드한 사진", use_container_width=True)

        if st.button("🔍 단어 추출 & 카드 만들기", type="primary", use_container_width=True):
            with st.spinner("사진에서 영단어를 찾는 중..."):
                words, raw_text = extract_words(image)
            st.session_state.raw_ocr_text = raw_text

            if not words:
                st.error("사진에서 영단어를 찾지 못했어요. 더 선명하고 글자가 큰 사진으로 다시 시도해보세요.")
            else:
                st.session_state.cards = build_cards(words)
                reset_quiz()
                st.success(f"{len(words)}개의 단어로 카드를 만들었어요!")

    if "raw_ocr_text" in st.session_state:
        with st.expander("🛠️ 디버그: OCR 원본 텍스트 보기"):
            st.text(st.session_state.raw_ocr_text or "(추출된 텍스트 없음)")

    if st.session_state.cards:
        st.divider()
        st.header("2. 추출된 단어 목록")
        for c in st.session_state.cards:
            st.write(f"- **{c['word']}** : {c['meaning']}")

# ---------------------------------------------------------------------------
# 메인 화면: 카드 퀴즈
# ---------------------------------------------------------------------------
if not st.session_state.cards:
    st.info("왼쪽 사이드바에서 사진을 업로드하고 카드를 만들어보세요 👈")
else:
    cards = st.session_state.cards
    total = len(cards)
    idx = st.session_state.idx
    card = cards[idx]

    st.progress((idx + 1) / total, text=f"{idx + 1} / {total}")

    if st.session_state.flipped:
        # 뒷면: 영단어
        st.markdown(
            f'<div class="flashcard card-word"><div>'
            f'<span class="card-label">영단어</span>{card["word"]}</div></div>',
            unsafe_allow_html=True,
        )
    else:
        # 앞면: 한국어 뜻
        st.markdown(
            f'<div class="flashcard card-meaning"><div>'
            f'<span class="card-label">뜻 (한국어)</span>{card["meaning"]}</div></div>',
            unsafe_allow_html=True,
        )

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("⬅️ 이전", use_container_width=True, disabled=(idx == 0)):
            st.session_state.idx -= 1
            st.session_state.flipped = False
            st.rerun()
    with col2:
        if st.button("🔄 카드 뒤집기", use_container_width=True):
            st.session_state.flipped = not st.session_state.flipped
            st.rerun()
    with col3:
        if st.button("다음 ➡️", use_container_width=True, disabled=(idx == total - 1)):
            st.session_state.idx += 1
            st.session_state.flipped = False
            st.rerun()

    st.divider()
    if st.button("🔁 처음부터 다시 풀기", use_container_width=True):
        reset_quiz()
        st.rerun()
