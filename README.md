# 📚 영단어 카드 퀴즈

영단어가 담긴 사진을 업로드하면 OCR로 단어를 추출하고, 각 단어를 한국어로 번역해
카드 앞면(영단어) / 뒷면(한국어 뜻)으로 넘겨보는 퀴즈 웹앱입니다.

## 1. 사전 준비: Tesseract OCR 설치

이 앱은 사진에서 글자를 읽기 위해 **Tesseract OCR 엔진**이 컴퓨터에 설치되어 있어야 합니다.
(파이썬 패키지인 `pytesseract`는 이 엔진을 호출하는 래퍼일 뿐, 엔진 자체는 별도 설치가 필요합니다.)

- **macOS (Homebrew)**
  ```bash
  brew install tesseract
  ```
- **Windows**
  1. https://github.com/UB-Mannheim/tesseract/wiki 에서 설치 파일 다운로드 후 설치
  2. 설치 후 `app.py` 상단에 아래 코드를 추가하고, 실제 설치 경로로 수정하세요.
     ```python
     import pytesseract
     pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
     ```
- **Ubuntu / Debian**
  ```bash
  sudo apt-get install tesseract-ocr tesseract-ocr-eng
  ```

## 2. 파이썬 패키지 설치

```bash
pip install -r requirements.txt
```

## 3. 앱 실행

```bash
streamlit run app.py
```

실행하면 브라우저가 자동으로 열리고 `http://localhost:8501` 에서 앱을 사용할 수 있습니다.

## 4. 사용 방법

1. 왼쪽 사이드바에서 영단어가 보이는 사진(png/jpg)을 업로드합니다.
2. **"🔍 단어 추출 & 카드 만들기"** 버튼을 누르면 사진 속 영단어를 자동으로 찾아내고,
   각 단어를 한국어로 번역해 카드를 만듭니다.
3. 화면 중앙의 카드에서:
   - **카드 뒤집기**: 영단어 ↔ 한국어 뜻 전환
   - **이전 / 다음**: 카드 넘기기
   - **처음부터 다시 풀기**: 1번 카드로 리셋
4. 사이드바 하단에서 추출된 전체 단어와 뜻 목록도 확인할 수 있습니다.

## 참고 사항

- 번역은 `deep-translator`(Google 번역 기반)를 사용하므로 인터넷 연결이 필요합니다.
- OCR 정확도는 사진 화질/글자 크기에 크게 좌우됩니다. 글자가 크고 선명하며 배경이
  단순한 사진일수록 인식률이 높습니다.
- 손글씨는 인식률이 낮을 수 있으니, 인쇄된 글자(교재, 단어장 등) 사진을 권장합니다.
