"""
영단어 카드 퀴즈 앱
- 사진/OCR 대신 영단어 목록 파일(txt/csv)을 업로드하거나 직접 입력
- 각 단어를 한국어로 번역
- 카드를 클릭하면 한국어 뜻 ↔ 영단어로 뒤집힘 (앞면: 한국어 뜻, 뒷면: 영단어)
실행 방법: streamlit run app.py
"""

import re
import streamlit as st
from deep_translator import GoogleTranslator

st.set_page_config(page_title="영단어 카드 퀴즈", page_icon="📚", layout="centered")

# ---------------------------------------------------------------------------
# 세션 상태 초기화
# ---------------------------------------------------------------------------
if "cards" not in st.session_state:
    st.session_state.cards = []  
if "idx" not in st.session_state:
    st.session_state.idx = 0
if "flipped" not in st.session_state:
    st.session_state.flipped = False


# ---------------------------------------------------------------------------
# 핵심 함수
# ---------------------------------------------------------------------------
def parse_words(text: str) -> list[str]:
    """텍스트에서 영단어를 추출하고 중복을 제거한다.
    한 줄에 한 단어를 권장하며, 쉼표/세미콜론/탭도 구분자로 사용할 수 있다.
    """
    raw = re.split(r"[\s,;]+", text)
    words, seen = [], set()

    for item in raw:
        word = item.strip()
        # 영단어와 하이픈/아포스트로피만 허용
        if not re.fullmatch(r"[A-Za-z]+(?:[-'][A-Za-z]+)*", word):
            continue

        word = word.lower()
        if len(word) < 2 or word in seen:
            continue

        seen.add(word)
        words.append(word)

    return words


@st.cache_data(show_spinner=False)
def translate_word(word: str) -> str:
    """영단어 하나를 한국어로 번역한다."""
    try:
        return GoogleTranslator(source="en", target="ko").translate(word)
    except Exception:
        return "(번역 실패)"


def build_cards(words: list[str]) -> list[dict]:
    cards = []
    progress = st.progress(0, text="단어 번역 중...")

    for i, word in enumerate(words):
        cards.append({
            "word": word,
            "meaning": translate_word(word),
        })
        progress.progress(
            (i + 1) / len(words),
            text=f"번역 중... ({i + 1}/{len(words)})"
        )

    progress.empty()
    return cards


def reset_quiz():
    st.session_state.idx = 0
    st.session_state.flipped = False


def flip_card():
    st.session_state.flipped = not st.session_state.flipped

# ---------------------------------------------------------------------------
# 카드 스타일 (CSS - 파란색 테마 및 세로 4배 확대)
# ---------------------------------------------------------------------------
CARD_CSS = """
<style>
/* Streamlit 기본 버튼을 4배 높이의 파란색 카드 스타일로 변경 */
div.stButton > button[key*="flashcard"] {
    min-height: 880px !important;  /* 기존 220px의 4배 */
    width: 100% !important;
    border-radius: 24px !important;
    font-size: 3em !important;
    font-weight: 800 !important;
    color: white !important;
    border: none !important;
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.2) !important;
    white-space: pre-wrap !important;
    word-break: break-word !important;
    transition: all 0.3s ease !important;
    margin: 10px 0px !important;
}

/* 카드 앞면 (한국어 뜻) - 짙은 신뢰감 있는 블루 그라데이션 */
div.stButton > button[key*="flashcard_front"] {
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%) !important;
}

/* 카드 뒷면 (영단어) - 화사한 파란색/보라빛 블루 그라데이션 */
div.stButton > button[key*="flashcard_back"] {
    background: linear-gradient(135deg, #00c6ff 0%, #0072ff 100%) !important;
}

div.stButton > button[key*="flashcard"]:hover {
    transform: translateY(-4px);
    box-shadow: 0 16px 36px rgba(0, 0, 0, 0.3) !important;
}

.card-hint {
    text-align: center;
    color: #4a5568;
    font-size: 0.95em;
    margin-bottom: 8px;
    font-weight: 600;
}
</style>
"""
st.markdown(CARD_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 제목
# ---------------------------------------------------------------------------
st.title("📚 영단어 카드 퀴즈")
st.caption("영단어 목록을 업로드하면 카드가 만들어집니다. 카드를 클릭하면 단어/뜻을 확인할 수 있어요.")

# ---------------------------------------------------------------------------
# 사이드바: 영단어 업로드
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("1. 영단어 업로드")

    uploaded_file = st.file_uploader(
        "TXT 또는 CSV 파일을 올려주세요",
        type=["txt", "csv"],
        help="한 줄에 한 단어를 넣거나, 쉼표/세미콜론으로 구분하세요."
    )

    if uploaded_file is not None:
        try:
            uploaded_text = uploaded_file.getvalue().decode("utf-8-sig")
        except UnicodeDecodeError:
            uploaded_text = uploaded_file.getvalue().decode("cp949", errors="ignore")

        if st.button("📚 단어로 카드 만들기", type="primary", use_container_width=True):
            words = parse_words(uploaded_text)

            if not words:
                st.error("영단어를 찾지 못했어요. 예: apple, book, computer")
            else:
                st.session_state.cards = build_cards(words)
                reset_quiz()
                st.success(f"{len(words)}개의 단어로 카드를 만들었어요!")

    st.caption("예시 파일:")
    st.code("apple\nbook\ncomputer\nbeautiful\nimportant", language="text")

    st.divider()
    st.header("또는 직접 입력")

    manual_words = st.text_area(
        "영단어 입력",
        placeholder="apple\nbook\ncomputer\nbeautiful",
        height=140,
        help="한 줄에 한 단어씩 입력하거나 쉼표로 구분하세요."
    )

    if st.button("✏️ 입력한 단어로 카드 만들기", use_container_width=True):
        words = parse_words(manual_words)

        if not words:
            st.error("영단어를 입력해주세요.")
        else:
            st.session_state.cards = build_cards(words)
            reset_quiz()
            st.success(f"{len(words)}개의 단어로 카드를 만들었어요!")

    if st.session_state.cards:
        st.divider()
        st.header("2. 단어 목록")
        for c in st.session_state.cards:
            st.write(f"- **{c['word']}** : {c['meaning']}")


# ---------------------------------------------------------------------------
# 메인 화면: 카드 퀴즈
# ---------------------------------------------------------------------------
if not st.session_state.cards:
    st.info("왼쪽에서 TXT/CSV 영단어 파일을 업로드하거나 직접 단어를 입력해 주세요. 👈")
else:
    cards = st.session_state.cards
    total = len(cards)
    idx = st.session_state.idx
    card = cards[idx]

    st.progress((idx + 1) / total, text=f"{idx + 1} / {total}")
    st.markdown(
        '<div class="card-hint">👆 카드를 클릭하면 뒤집힙니다 (앞면: 뜻 / 뒷면: 영단어)</div>',
        unsafe_allow_html=True,
    )

    # 앞면: 한국어 뜻 / 뒷면: 영단어
    if not st.session_state.flipped:
        label = f"🇰🇷 {card['meaning']}"
        key_suffix = "front"
    else:
        label = f"🔤 {card['word']}"
        key_suffix = "back"

    if st.button(
        label,
        key=f"flashcard_{idx}_{key_suffix}",
        use_container_width=True,
    ):
        flip_card()
        st.rerun()

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button(
            "⬅️ 이전",
            use_container_width=True,
            disabled=(idx == 0),
        ):
            st.session_state.idx -= 1
            st.session_state.flipped = False
            st.rerun()

    with col2:
        if st.button("🔄 뒤집기", use_container_width=True):
            flip_card()
            st.rerun()

    with col3:
        if st.button(
            "다음 ➡️",
            use_container_width=True,
            disabled=(idx == total - 1),
        ):
            st.session_state.idx += 1
            st.session_state.flipped = False
            st.rerun()

    st.divider()

    if st.button("🔁 처음부터 다시 풀기", use_container_width=True):
        reset_quiz()
        st.rerun()
