````python
"""
영단어 카드 퀴즈 앱

기능
- 사진 업로드 없이 영단어 : 한국어 뜻을 직접 입력
- 여러 단어를 한 번에 등록 가능
- 카드 앞면: 영어 단어
- 카드 클릭: 카드 뒤집기
- 카드 뒷면: 한국어 뜻 + 입력한 영단어 채점
- 이전 / 다음 단어
- 단어 순서 섞기

실행 방법:
streamlit run app.py
"""

import re
import random
import streamlit as st


# ============================================================
# 페이지 설정
# ============================================================

st.set_page_config(
    page_title="영단어 카드 퀴즈",
    page_icon="📚",
    layout="centered",
)


# ============================================================
# 세션 상태 초기화
# ============================================================

if "cards" not in st.session_state:
    st.session_state.cards = []

if "idx" not in st.session_state:
    st.session_state.idx = 0

if "flipped" not in st.session_state:
    st.session_state.flipped = False

if "user_answer" not in st.session_state:
    st.session_state.user_answer = ""


# ============================================================
# 함수
# ============================================================

def parse_word_pairs(text: str) -> list[dict]:
    """
    입력된 텍스트에서
    단어 : 뜻
    형식의 데이터를 추출한다.
    """

    lines = text.strip().splitlines()

    cards = []
    seen = set()

    for line in lines:
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

        word_key = word.lower()

        # 중복 제거
        if word_key in seen:
            continue

        seen.add(word_key)

        cards.append({
            "word": word,
            "meaning": meaning,
        })

    return cards


def reset_quiz():
    """퀴즈 처음으로 초기화"""

    st.session_state.idx = 0
    st.session_state.flipped = False
    st.session_state.user_answer = ""


def shuffle_quiz():
    """단어 순서를 섞는다."""

    random.shuffle(st.session_state.cards)

    reset_quiz()


def flip_card():
    """카드를 뒤집는다."""

    st.session_state.flipped = not st.session_state.flipped


def next_card():
    """다음 카드"""

    if st.session_state.idx < len(st.session_state.cards) - 1:
        st.session_state.idx += 1
        st.session_state.flipped = False
        st.session_state.user_answer = ""


def previous_card():
    """이전 카드"""

    if st.session_state.idx > 0:
        st.session_state.idx -= 1
        st.session_state.flipped = False
        st.session_state.user_answer = ""


# ============================================================
# CSS
# ============================================================

CARD_CSS = """
<style>

.flashcard {
    width: 100%;
    min-height: 280px;

    border-radius: 24px;

    display: flex;
    align-items: center;
    justify-content: center;

    text-align: center;

    padding: 40px;

    margin: 20px 0;

    font-size: 2.4em;
    font-weight: 700;

    box-shadow:
        0 10px 30px rgba(0, 0, 0, 0.18);

    word-break: break-word;

    transition: transform 0.2s ease;
}

.card-front {
    background:
        linear-gradient(
            135deg,
            #667eea 0%,
            #764ba2 100%
        );

    color: white;
}

.card-back {
    background:
        linear-gradient(
            135deg,
            #11998e 0%,
            #38ef7d 100%
        );

    color: white;
}

.card-label {
    font-size: 0.32em;
    opacity: 0.85;
    display: block;
    margin-bottom: 12px;
    font-weight: 400;
}

.answer-result {
    font-size: 0.42em;
    margin-top: 20px;
    font-weight: 600;
}

</style>
"""

st.markdown(CARD_CSS, unsafe_allow_html=True)


# ============================================================
# 사이드바
# ============================================================

with st.sidebar:

    st.header("📚 영단어 등록")

    manual_words = st.text_area(
        "단어 : 뜻 입력",
        placeholder=(
            "apple : 사과\n"
            "book : 책\n"
            "computer : 컴퓨터\n"
            "beautiful : 아름다운"
        ),
        height=220,
        help="한 줄에 하나씩 '영단어 : 한국어 뜻' 형식으로 입력하세요.",
    )

    if st.button(
        "✏️ 단어로 카드 만들기",
        use_container_width=True,
    ):

        cards = parse_word_pairs(manual_words)

        if not cards:

            st.error("단어와 뜻을 입력해주세요.")

        else:

            st.session_state.cards = cards

            shuffle_quiz()

            st.success(
                f"{len(cards)}개의 단어가 등록되었습니다!"
            )

    # --------------------------------------------------------
    # 단어 목록
    # --------------------------------------------------------

    if st.session_state.cards:

        st.divider()

        st.header("📝 단어 목록")

        for i, c in enumerate(st.session_state.cards, start=1):

            st.write(
                f"{i}. **{c['word']}** : {c['meaning']}"
            )

        st.divider()

        if st.button(
            "🔀 단어 순서 섞기",
            use_container_width=True,
        ):

            shuffle_quiz()

            st.rerun()


# ============================================================
# 메인 화면
# ============================================================

st.title("📚 영단어 카드 퀴즈")

st.caption(
    "영단어를 입력하고 카드를 클릭해서 정답을 확인하세요."
)


# ============================================================
# 카드가 없는 경우
# ============================================================

if not st.session_state.cards:

    st.info(
        "👈 왼쪽 사이드바에서 영단어와 뜻을 입력해주세요."
    )

    st.markdown(
        """
        ### 입력 예시

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
# 현재 카드 정보
# ============================================================

cards = st.session_state.cards

idx = st.session_state.idx

total = len(cards)

card = cards[idx]

word = card["word"]

meaning = card["meaning"]


# ============================================================
# 진행 상황
# ============================================================

st.progress(
    (idx + 1) / total
)

st.write(
    f"### {idx + 1} / {total}"
)


# ============================================================
# 영단어 입력
# ============================================================

user_input = st.text_input(
    "✍️ 영단어를 입력하세요",
    key=f"answer_{idx}",
    placeholder="예: apple",
)


# ============================================================
# 정답 판정
# ============================================================

clean_input = user_input.strip().lower()

clean_target = word.strip().lower()

if clean_input:

    if clean_input == clean_target:

        ox_result = "⭕ 정답입니다!"

    else:

        ox_result = (
            f"❌ 오답입니다!"
            f"<br>"
            f"정답: <b>{word}</b>"
        )

else:

    ox_result = "💡 먼저 영단어를 입력해 주세요."


# ============================================================
# 카드
# ============================================================

if not st.session_state.flipped:

    # --------------------------------------------------------
    # 카드 앞면
    # --------------------------------------------------------

    card_text = f"""
    <div class="flashcard card-front">
        <div>
            <span class="card-label">
                영어 단어
            </span>
            {word}
        </div>
    </div>
    """

else:

    # --------------------------------------------------------
    # 카드 뒷면
    # --------------------------------------------------------

    card_text = f"""
    <div class="flashcard card-back">
        <div>
            <span class="card-label">
                한국어 뜻
            </span>

            {meaning}

            <div class="answer-result">
                {ox_result}
            </div>
        </div>
    </div>
    """


# ============================================================
# 카드 클릭
# ============================================================

st.markdown(card_text, unsafe_allow_html=True)

if st.button(
    "🔄 카드 뒤집기",
    use_container_width=True,
):

    flip_card()

    st.rerun()


# ============================================================
# 이전 / 다음
# ============================================================

col1, col2, col3 = st.columns([1, 1, 1])


with col1:

    if st.button(
        "⬅️ 이전",
        use_container_width=True,
        disabled=(idx == 0),
    ):

        previous_card()

        st.rerun()


with col2:

    if st.button(
        "🔀 섞기",
        use_container_width=True,
    ):

        shuffle_quiz()

        st.rerun()


with col3:

    if st.button(
        "다음 ➡️",
        use_container_width=True,
        disabled=(idx == total - 1),
    ):

        next_card()

        st.rerun()


# ============================================================
# 사용 방법
# ============================================================

st.divider()

st.caption(
    "💡 영어 단어를 입력한 후 카드를 클릭하면 한국어 뜻과 정답 여부를 확인할 수 있습니다."
)
````
