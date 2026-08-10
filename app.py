"""
영단어 카드 퀴즈 앱 (스펠링 테스트 기능 포함)
- [단어 : 뜻] 목록 파일(txt/csv) 업로드 또는 직접 입력
- 앞면: 한국어 뜻 표시
- 아래쪽: 영단어 스펠링 입력 칸 (정답 체크: OK / ERROR)
실행 방법: streamlit run app.py
"""

import re
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
    """텍스트에서 [단어 : 뜻] 쌍을 추출하고 중복을 제거한다.
    구분자로 콜론(:), 등호(=), 하이픈(-), 쉼표(,), 탭(\t)을 인식합니다.
    """
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


def flip_card():
    st.session_state.flipped = not st.session_state.flipped


# ---------------------------------------------------------------------------
# 카드 스타일 (CSS - 파란색 테마 및 OK/ERROR 스타일)
# ---------------------------------------------------------------------------
CARD_CSS = """
<style>
/* 카드 컨테이너 */
.card-container {
    width: 100%;
    min-height: 300px !important;
    border-radius: 24px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 40px;
    margin: 15px 0 20px 0;
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.2);
    word-break: break-word;
    transition: all 0.3s ease;
}

.card-container:hover {
    transform: translateY(-4px);
    box-shadow: 0 18px 40px rgba(0, 0, 0, 0.3);
}

/* 카드 앞면 (한국어 뜻) */
.card-front {
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    color: #ffffff;
}

/* 카드 뒷면 (영단어) */
.card-back {
    background: linear-gradient(135deg, #00c6ff 0%, #0072ff 100%);
    color: #ffffff;
}

.card-label-sub {
    font-size: 1.3rem;
    opacity: 0.85;
    margin-bottom: 24px;
    font-weight: 300;
}

.card-text-main {
    font-size: 3.8rem;
    font-weight: 300;
    line-height: 1.3;
}

/* 정답/오답 텍스트 스타일 */
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
st.caption("단어와 뜻 목록을 입력하고, 스펠링을 맞춰보세요!")

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
                reset_quiz()
                st.success(f"{len(cards)}개의 단어로 카드를 만들었어요!")

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
            reset_quiz()
            st.success(f"{len(cards)}개의 단어로 카드를 만들었어요!")

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

    # 앞면: 한국어 뜻 / 뒷면: 영단어 설정
    if not st.session_state.flipped:
        sub_label = "🇰🇷 한국어 뜻 (앞면)"
        main_text = card["meaning"]
        card_class = "card-front"
    else:
        sub_label = "🔤 영단어 정답 (뒷면)"
        main_text = card["word"]
        card_class = "card-back"

    # 세로 카드 HTML 영역
    card_html = f"""
    <div class="card-container {card_class}">
        <div class="card-label-sub">{sub_label}</div>
        <div class="card-text-main">{main_text}</div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

    # -----------------------------------------------------------------------
    # 영단어 스펠링 입력 및 정답 확인 영역
    # -----------------------------------------------------------------------
    user_input = st.text_input(
        "✍️ 영단어 스펠링을 입력하세요 (입력 후 Enter):",
        key=f"input_{idx}",
        placeholder="예: apple",
    )

    if user_input:
        clean_input = user_input.strip().lower()
        clean_target = card["word"].strip().lower()

        if clean_input == clean_target:
            st.markdown('<div class="status-ok">⭕ OK</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-error">❌ ERROR</div>', unsafe_allow_html=True)

    st.write("")

    # 하단 조작 버튼
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
        if st.button("🔄 정답 보기 / 뒤집기", type="primary", use_container_width=True):
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
