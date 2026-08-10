"""
영단어 카드 퀴즈 앱
- 사진을 업로드하면 OCR로 영단어를 추출
- 각 단어를 한국어로 번역
- 카드 앞면(영단어) / 뒷면(한국어 뜻)으로 넘겨보는 퀴즈 UI
실행 방법: streamlit run app.py
"""


import re
import random
import streamlit as st

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
def parse_word_pairs(text: str) -> list[dict]:
    """텍스트에서 [단어 : 뜻] 쌍을 추출하고 중복을 제거한다."""
    lines = text.strip().splitlines()
    cards, seen = [], set()

    for line in lines:
        line = line.strip()
        if not line:
            continue

        parts = re.split(r"[:=\-\t,]", line, maxsplit=1)

        word = parts[0].strip()
        meaning = parts[1].strip() if len(parts) > 1 and parts[1].strip() else word

        if not word:
            continue

        word_key = word.lower()
        if word_key in seen:
            continue

        seen.add(word_key)
        cards.append({
            "word": word,
            "meaning": meaning
        })

    return cards


def reset_quiz():
    st.session_state.idx = 0
    st.session_state.flipped = False


def shuffle_quiz():
    random.shuffle(st.session_state.cards)
    reset_quiz()


def flip_card():
    st.session_state.flipped = not st.session_state.flipped

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
with st.sidebar:
    st.header("1. 단어 : 뜻 업로드")

    manual_words = st.text_area(
        "단어 : 뜻 입력",
        placeholder="apple : 사과\nbook : 책\ncomputer : 컴퓨터",
        height=180,
        help="한 줄에 '단어 : 뜻' 형식으로 작성해 주세요."
    )

    if st.button("✏️ 입력한 단어로 카드 만들기", use_container_width=True):
        cards = parse_word_pairs(manual_words)

        if not cards:
            st.error("단어와 뜻을 입력해주세요.")
        else:
            st.session_state.cards = cards
            shuffle_quiz()
            st.success(f"{len(cards)}개의 단어로 카드를 만들었어요! (순서 섞음)")

    if st.session_state.cards:
        st.divider()
        st.header("2. 단어 목록")
        for c in st.session_state.cards:
            st.write(f"- **{c['word']}** : {c['meaning']}")

    if st.session_state.cards:
        # 카드가 방금 새로 만들어졌을 수도 있으므로, 여기서 다시 계산합니다.
        idx = st.session_state.idx
        total = len(st.session_state.cards)
        card = st.session_state.cards[idx]

        # -----------------------------------------------------------------------
        # 1. 영단어 스펠링 입력창 (카드 상단 또는 하단 배치)
        # -----------------------------------------------------------------------
        user_input = st.text_input(
            "✍️ 단어 입력하세요 (입력 후 카드 클릭):",
            key=f"input_{idx}",
            placeholder="예: apple",
        )

        # 채점 결과 계산
        clean_input = user_input.strip().lower() if user_input else ""
        clean_target = card["word"].strip().lower()

        if not clean_input:
            ox_result = "❌ 오답입니다!"
        elif clean_input == clean_target:
            ox_result = "⭕ (정답입니다!)"
        else:
            ox_result = f"❌ 오답입니다! (입력: {user_input})"

        # -----------------------------------------------------------------------
        # 2. 클릭 시 뒤집히는 카드 (Streamlit Button 기반)
        # -----------------------------------------------------------------------
        if not st.session_state.flipped:
            # 카드 앞면
            card_label = (
                f"{card['meaning']}\n\n\n"
            )
            card_key = f"main_card_btn_front_{idx}"
        else:
            # 카드 뒷면 (정답 + O/X 표기)
            card_label = (
                f"{card['word']}\n\n"
                f"{ox_result}\n"
            )
            card_key = f"main_card_btn_back_{idx}"

        # 카드 클릭 이벤트 처리
        if st.button(card_label, key=card_key, use_container_width=True):
            flip_card()
            st.rerun()

        st.write("")

        # -----------------------------------------------------------------------
        # 3. 하단 이전/다음/섞기 조작 버튼
        # -----------------------------------------------------------------------
        col1, col2 = st.columns([1, 1])

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
            if st.button(
                "다음 ➡️",
                use_container_width=True,
                disabled=(idx == total - 1),
            ):
                st.session_state.idx += 1
                st.session_state.flipped = False
                st.rerun()
