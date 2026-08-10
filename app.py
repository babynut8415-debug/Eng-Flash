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

st.set_page_config(page_title="영단어 카드 퀴즈", page_icon="📚", layout="centered")

# ---------------------------------------------------------------------------
# 세션 상태
# ---------------------------------------------------------------------------
if "cards" not in st.session_state:
    st.session_state.cards = []
if "idx" not in st.session_state:
    st.session_state.idx = 0
if "flipped" not in st.session_state:
    st.session_state.flipped = False


# ---------------------------------------------------------------------------
# 단어 처리
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
# 카드 CSS
# ---------------------------------------------------------------------------
CARD_CSS = """
<style>
.card-hint {
    text-align: center;
    color: #777;
    font-size: 0.9rem;
    margin: 4px 0 12px 0;
}

div[data-testid="stButton"] > button.card-button {
    width: 100%;
    min-height: 260px;
    border-radius: 20px;
    padding: 30px;
    margin: 10px 0 20px 0;
    font-size: 2.2rem;
    font-weight: 700;
    white-space: normal;
    word-break: break-word;
    box-shadow: 0 8px 24px rgba(0,0,0,.15);
    transition: transform .12s ease, box-shadow .12s ease;
}

div[data-testid="stButton"] > button.card-button:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 30px rgba(0,0,0,.20);
}

div[data-testid="stButton"] > button.card-word {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    color: white;
    border: none;
}

div[data-testid="stButton"] > button.card-meaning {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
}
</style>
"""
st.markdown(CARD_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 제목
# ---------------------------------------------------------------------------
st.title("📚 영단어 카드 퀴즈")
st.caption("영단어 목록을 업로드하면 카드가 만들어집니다. 카드를 클릭하면 뜻을 확인할 수 있어요.")

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
# 메인: 카드
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
        '<div class="card-hint">👆 카드를 클릭하면 뒤집힙니다</div>',
        unsafe_allow_html=True,
    )

    # Streamlit 버튼을 카드처럼 꾸며서 카드 자체를 클릭하면 뒤집히도록 처리
    if st.session_state.flipped:
        label = card["meaning"]
        card_class = "card-meaning"
    else:
        label = card["word"]
        card_class = "card-word"

    if st.button(
        label,
        key=f"flashcard_{idx}_{st.session_state.flipped}",
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
