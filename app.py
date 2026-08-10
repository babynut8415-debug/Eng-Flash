"""
영단어 카드 퀴즈 앱 (카드 직접 클릭 뒤집기 + O/X 표기)
- [단어 : 뜻] 목록 파일(txt/csv) 업로드 또는 직접 입력
- 카드 직접 클릭 시 뒤집힘
- 뒤집히면 영단어 정답 및 O / X 표기
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
    st.session_state.cards = []  
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
# 카드 및 입력창 스타일 (CSS)
# ---------------------------------------------------------------------------
CARD_CSS = """
<style>
/* 1. 카드로 사용할 대형 버튼 스타일링 */
div.stButton > button[key*="main_card_btn"] {
    width: 100% !important;
    min-height: 320px !important;
    border-radius: 20px !important;
    padding: 30px !important;
    margin: 10px 0 20px 0 !important;
    border: none !important;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15) !important;
    transition: all 0.3s ease !important;
    white-space: pre-wrap !important;
    font-size: 1.3rem !important;
    font-weight: 700 !important;
    line-height: 1.8 !important;
}

div.stButton > button[key*="main_card_btn"]:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.25) !important;
}

/* 카드 앞면 스타일 (짙은 파란색) */
div.stButton > button[key*="main_card_btn_front"] {
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%) !important;
    color: #ffffff !important;
}

/* 카드 뒷면 스타일 (밝은 파란색) */
div.stButton > button[key*="main_card_btn_back"] {
    background: linear-gradient(135deg, #00c6ff 0%, #0072ff 100%) !important;
    color: #ffffff !important;
}

/* 2. 스펠링 입력창 및 텍스트 크기 2배 확대 */
div[data-testid="stTextInput"] input {
    font-size: 2rem !important;
    height: 80px !important;
    border-radius: 12px !important;
    padding: 10px 20px !important;
    font-weight: 600 !important;
}

div[data-testid="stTextInput"] label p {
    font-size: 1.3rem !important;
    font-weight: bold !important;
}

/* 하단 O/X 상태 표시 */
.status-ok {
    color: #2e7d32;
    font-size: 2.2rem;
    font-weight: 900;
    text-align: center;
    margin: 10px 0;
}

.status-error {
    color: #c62828;
    font-size: 2.2rem;
    font-weight: 900;
    text-align: center;
    margin: 10px 0;
}
</style>
"""
st.markdown(CARD_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 제목
# ---------------------------------------------------------------------------
st.title("📚 영단어 카드 퀴즈")
st.caption("단어와 뜻 목록을 입력하고, 스펠링을 입력한 뒤 카드를 클릭해 정답을 확인하세요!")

# ---------------------------------------------------------------------------
# 사이드바: 영단어 업로드
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("1. 단어 : 뜻 업로드")

    uploaded_file = st.file_uploader(
        "TXT 또는 CSV 파일을 올려주세요",
        type=["txt", "csv"],
        help="'단어 : 뜻' 형식으로 작성해 주세요."
    )

    if uploaded_file is not None:
        try:
            uploaded_text = uploaded_file.getvalue().decode("utf-8-sig")
        except UnicodeDecodeError:
            uploaded_text = uploaded_file.getvalue().decode("cp949", errors="ignore")

        if st.button("📚 단어로 카드 만들기", type="primary", use_container_width=True):
            cards = parse_word_pairs(uploaded_text)

            if not cards:
                st.error("단어를 찾지 못했어요. 'apple : 사과' 형태로 입력해 주세요.")
            else:
                st.session_state.cards = cards
                shuffle_quiz()
                st.success(f"{len(cards)}개의 단어로 카드를 만들었어요! (순서 섞음)")

    st.caption("예시 파일:")
    st.code("apple : 사과\nbook : 책\ncomputer : 컴퓨터\nbeautiful : 아름다운\nimportant : 중요한", language="text")

    st.divider()
    st.header("또는 직접 입력")

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


# ---------------------------------------------------------------------------
# 메인 화면: 카드 퀴즈
# ---------------------------------------------------------------------------
if not st.session_state.cards:
    st.info("왼쪽에서 TXT/CSV 단어 파일('단어 : 뜻' 형식)을 업로드하거나 직접 입력해 주세요. 👈")
else:
    cards = st.session_state.cards
    total = len(cards)
    idx = st.session_state.idx
    card = cards[idx]

    st.progress((idx + 1) / total, text=f"{idx + 1} / {total}")

    # -----------------------------------------------------------------------
    # 1. 영단어 스펠링 입력창 (카드 상단 또는 하단 배치)
    # -----------------------------------------------------------------------
    user_input = st.text_input(
        "✍️ 영단어 스펠링을 입력하세요 (입력 후 카드를 클릭하세요):",
        key=f"input_{idx}",
        placeholder="예: apple",
    )

    # 채점 결과 계산
    clean_input = user_input.strip().lower() if user_input else ""
    clean_target = card["word"].strip().lower()

    if not clean_input:
        ox_result = "❓ 미입력"
    elif clean_input == clean_target:
        ox_result = "⭕ O (정답입니다!)"
    else:
        ox_result = f"❌ X (입력: {user_input})"

    # -----------------------------------------------------------------------
    # 2. 클릭 시 뒤집히는 카드 (Streamlit Button 기반)
    # -----------------------------------------------------------------------
    if not st.session_state.flipped:
        # 카드 앞면
        card_label = (
            f"🇰🇷 한국어 뜻 (앞면)\n\n"
            f"{card['meaning']}\n\n\n"
            f"👇 (카드를 클릭하면 정답과 O/X 결과가 나옵니다)"
        )
        card_key = f"main_card_btn_front_{idx}"
    else:
        # 카드 뒷면 (정답 + O/X 표기)
        card_label = (
            f"🔤 영단어 정답 (뒷면)\n\n"
            f"정답: {card['word']}\n"
            f"판정: {ox_result}\n\n\n"
            f"👇 (카드를 클릭하면 앞면으로 돌아갑니다)"
        )
        card_key = f"main_card_btn_back_{idx}"

    # 카드 클릭 이벤트 처리
    if st.button(card_label, key=card_key, use_container_width=True):
        flip_card()
        st.rerun()

    # 입력창 바로 밑에 실시간 O/X 상태 안내
    if user_input:
        if clean_input == clean_target:
            st.markdown('<div class="status-ok">⭕ O</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-error">❌ X</div>', unsafe_allow_html=True)

    st.write("")

    # -----------------------------------------------------------------------
    # 3. 하단 이전/다음/섞기 조작 버튼
    # -----------------------------------------------------------------------
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
        if st.button("🔄 뒤집기 (버튼)", type="primary", use_container_width=True):
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

    col_sub1, col_sub2 = st.columns(2)
    with col_sub1:
        if st.button("🔀 단어 섞기 (랜덤)", use_container_width=True):
            shuffle_quiz()
            st.toast("🎲 카드 순서를 랜덤하게 섞었습니다!")
            st.rerun()

    with col_sub2:
        if st.button("🔁 처음부터 다시 풀기", use_container_width=True):
            reset_quiz()
            st.rerun()
