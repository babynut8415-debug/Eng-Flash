import re
import random
import streamlit as st


# ============================================================
# 페이지 설정
# ============================================================

st.set_page_config(
    page_title="영단어 카드 퀴즈",
    page_icon="📚",
    layout="centered"
)


# ============================================================
# 세션 상태
# ============================================================

if "cards" not in st.session_state:
    st.session_state.cards = []

if "idx" not in st.session_state:
    st.session_state.idx = 0

if "flipped" not in st.session_state:
    st.session_state.flipped = False


# ============================================================
# 단어 파싱
# ============================================================

def parse_word_pairs(text):
    cards = []
    seen = set()

    for line in text.strip().splitlines():

        line = line.strip()

        if not line:
            continue

        # 지원 형식
        # apple : 사과
        # apple = 사과
        # apple, 사과
        # apple    사과
        parts = re.split(r"[:=\t,]", line, maxsplit=1)

        word = parts[0].strip()

        if len(parts) > 1:
            meaning = parts[1].strip()
        else:
            meaning = ""

        if not word:
            continue

        key = word.lower()

        if key in seen:
            continue

        seen.add(key)

        cards.append({
            "word": word,
            "meaning": meaning
        })

    return cards


# ============================================================
# 퀴즈 함수
# ============================================================

def reset_quiz():
    st.session_state.idx = 0
    st.session_state.flipped = False


def shuffle_quiz():
    random.shuffle(st.session_state.cards)
    reset_quiz()


def previous_card():
    if st.session_state.idx > 0:
        st.session_state.idx -= 1
        st.session_state.flipped = False


def next_card():
    if st.session_state.idx < len(st.session_state.cards) - 1:
        st.session_state.idx += 1
        st.session_state.flipped = False


def flip_card():
    st.session_state.flipped = not st.session_state.flipped


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    /* 카드 버튼 */
    div.stButton > button[kind="secondary"] {
        width: 100%;
        min-height: 280px;
        border-radius: 25px;
        border: none;
        font-size: 40px;
        font-weight: 700;
        white-space: pre-wrap;
        box-shadow: 0 8px 25px rgba(0,0,0,0.18);
        transition: all 0.2s ease;
    }

    div.stButton > button[kind="secondary"]:hover {
        transform: scale(1.02);
        box-shadow: 0 12px 30px rgba(0,0,0,0.25);
    }

    .front-info {
        text-align: center;
        color: #777;
        margin-bottom: 10px;
    }

    .back-info {
        text-align: center;
        color: #777;
        margin-bottom: 10px;
    }

    .correct {
        color: #00a651;
        font-size: 22px;
        font-weight: bold;
        text-align: center;
    }

    .wrong {
        color: #e53935;
        font-size: 22px;
        font-weight: bold;
        text-align: center;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 제목
# ============================================================

st.title("📚 영단어 카드 퀴즈")

st.caption(
    "영단어를 입력하고 카드를 클릭해서 정답을 확인하세요."
)


# ============================================================
# 사이드바 - 단어 입력
# ============================================================

with st.sidebar:

    st.header("📝 영단어 등록")

    manual_words = st.text_area(
        "단어 : 뜻 입력",
        placeholder=(
            "apple : 사과\n"
            "book : 책\n"
            "computer : 컴퓨터\n"
            "beautiful : 아름다운"
        ),
        height=220
    )

    if st.button(
        "✏️ 단어로 카드 만들기",
        use_container_width=True
    ):

        cards = parse_word_pairs(manual_words)

        if not cards:

            st.error("단어와 뜻을 입력해주세요.")

        else:

            st.session_state.cards = cards

            shuffle_quiz()

            st.success(
                f"{len(cards)}개의 단어가 등록되었습니다."
            )

    # --------------------------------------------------------
    # 단어 목록
    # --------------------------------------------------------

    if st.session_state.cards:

        st.divider()

        st.subheader("📖 등록된 단어")

        for i, item in enumerate(
            st.session_state.cards,
            start=1
        ):

            st.write(
                f"{i}. **{item['word']}** : {item['meaning']}"
            )


# ============================================================
# 카드가 없는 경우
# ============================================================

if not st.session_state.cards:

    st.info(
        "👈 왼쪽 메뉴에서 영단어와 한국어 뜻을 입력해주세요."
    )

    st.markdown(
        """
        ### 입력 방법

        아래처럼 입력하면 됩니다.

        ```
        apple : 사과
        book : 책
        computer : 컴퓨터
        beautiful : 아름다운
        ```
        """
    )

    st.stop()


# ============================================================
# 현재 카드
# ============================================================

cards = st.session_state.cards

idx = st.session_state.idx

total = len(cards)

card = cards[idx]

word = card["word"]

meaning = card["meaning"]


# ============================================================
# 진행률
# ============================================================

st.progress((idx + 1) / total)

st.markdown(
    f"### 카드 {idx + 1} / {total}"
)


# ============================================================
# 영단어 입력
# ============================================================

user_input = st.text_input(
    "✍️ 영단어를 입력하세요",
    placeholder="예: apple",
    key=f"user_answer_{idx}"
)


# ============================================================
# 정답 확인
# ============================================================

input_word = user_input.strip().lower()

correct_word = word.strip().lower()

if input_word == correct_word and input_word:

    result = "⭕ 정답입니다!"
    result_class = "correct"

elif input_word:

    result = f"❌ 오답입니다!  정답: {word}"
    result_class = "wrong"

else:

    result = ""


# ============================================================
# 카드
# ============================================================

if not st.session_state.flipped:

    # --------------------------------------------------------
    # 앞면
    # --------------------------------------------------------

    st.markdown(
        '<div class="front-info">영단어를 보고 뜻을 생각해보세요</div>',
        unsafe_allow_html=True
    )

    card_text = f"📚\n\n{word}"

else:

    # --------------------------------------------------------
    # 뒷면
    # --------------------------------------------------------

    st.markdown(
        '<div class="back-info">한국어 뜻</div>',
        unsafe_allow_html=True
    )

    card_text = f"🇰🇷\n\n{meaning}"


# ============================================================
# 카드 클릭
# ============================================================

if st.button(
    card_text,
    key=f"card_{idx}_{st.session_state.flipped}",
    use_container_width=True
):

    flip_card()

    st.rerun()


# ============================================================
# 뒷면일 때 채점 결과 표시
# ============================================================

if st.session_state.flipped and result:

    st.markdown(
        f'<div class="{result_class}">{result}</div>',
        unsafe_allow_html=True
    )


# ============================================================
# 안내
# ============================================================

st.caption(
    "👆 카드를 클릭하면 앞면과 뒷면이 바뀝니다."
)


# ============================================================
# 조작 버튼
# ============================================================

col1, col2, col3 = st.columns(3)


with col1:

    if st.button(
        "⬅️ 이전",
        use_container_width=True,
        disabled=(idx == 0)
    ):

        previous_card()

        st.rerun()


with col2:

    if st.button(
        "🔀 섞기",
        use_container_width=True
    ):

        shuffle_quiz()

        st.rerun()


with col3:

    if st.button(
        "다음 ➡️",
        use_container_width=True,
        disabled=(idx == total - 1)
    ):

        next_card()

        st.rerun()
