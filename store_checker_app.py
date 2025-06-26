import streamlit as st
from datetime import datetime
import gspread
import tempfile
from PIL import Image

# 📄 인증 (gspread + st.secrets)
gc = gspread.service_account_from_dict(st.secrets["gdrive_credentials"])

# 📄 구글 시트 열기
SHEET_ID = "1ZpWTwJUjEWnMfQK7AICXANFV9BMSo_6JsZhVsatjVdM"
SHEET_NAME = "시트1"
worksheet = gc.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

# UI 구성
st.title("📸 매장 진열 사진 등록")

brands = ["테팔", "필립스", "락앤락", "도루코", "기타"]
categories = ["주방", "생활용품", "가전", "세제", "기타"]

# 사진 업로드
col1, col2, col3 = st.columns(3)
with col1:
    full_photo = st.file_uploader("전체 진열사진", type=["jpg", "jpeg", "png"], key="full")
with col2:
    line1_photo = st.file_uploader("1번 줄 사진", type=["jpg", "jpeg", "png"], key="line1")
with col3:
    line2_photo = st.file_uploader("2번 줄 사진", type=["jpg", "jpeg", "png"], key="line2")

# 정보 입력
line1 = st.text_input("1번 줄 제품명")
line2 = st.text_input("2번 줄 제품명")
brand = st.selectbox("브랜드 선택", brands)
category = st.selectbox("카테고리 선택", categories)

# 제출
if st.button("제출하기"):
    if full_photo and line1_photo and line2_photo:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 사진은 현재 구글 드라이브에 안 올림 (링크 필요 시 아래 참고)
        worksheet.append_row([
            now, "사진 링크 없음", "사진 링크 없음", "사진 링크 없음",
            line1, line2, brand, category
        ])
        st.success("✅ 제출 완료! 구글 시트에 저장되었습니다.")
    else:
        st.warning("⚠️ 모든 사진을 업로드해주세요.")
