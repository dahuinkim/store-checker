import streamlit as st
import pandas as pd
from openpyxl import load_workbook, Workbook
from openpyxl.drawing.image import Image as XLImage
from PIL import Image
import os
from datetime import datetime

# 폴더 생성
if not os.path.exists("photos"):
    os.makedirs("photos")
if not os.path.exists("output"):
    os.makedirs("output")

EXCEL_PATH = "output/store_checker_data.xlsx"

# 브랜드와 카테고리 옵션
brands = ["테팔", "필립스", "락앤락", "도루코", "기타"]
categories = ["주방", "생활용품", "가전", "세제", "기타"]

st.title("매장 진열 사진 입력 앱")

# 사진 입력 (3종)
st.subheader("📸 사진 업로드")
col1, col2, col3 = st.columns(3)
with col1:
    full_photo = st.file_uploader("전체 진열사진", type=["jpg", "jpeg", "png"], key="full")
with col2:
    line1_photo = st.file_uploader("1번줄 사진", type=["jpg", "jpeg", "png"], key="line1")
with col3:
    line2_photo = st.file_uploader("2번줄 사진", type=["jpg", "jpeg", "png"], key="line2")

# 텍스트 입력
st.subheader("📝 제품 정보 입력")
line1 = st.text_input("1번 줄 제품명")
line2 = st.text_input("2번 줄 제품명")
brand = st.selectbox("브랜드 선택", brands)
category = st.selectbox("카테고리 선택", categories)

if st.button("제출하기"):
    if full_photo and line1_photo and line2_photo:
        now = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 파일 저장
        full_path = f"photos/full_{now}.jpg"
        line1_path = f"photos/line1_{now}.jpg"
        line2_path = f"photos/line2_{now}.jpg"
        with open(full_path, "wb") as f:
            f.write(full_photo.getbuffer())
        with open(line1_path, "wb") as f:
            f.write(line1_photo.getbuffer())
        with open(line2_path, "wb") as f:
            f.write(line2_photo.getbuffer())

        # 엑셀 열기 or 생성
        if os.path.exists(EXCEL_PATH):
            wb = load_workbook(EXCEL_PATH)
            ws = wb.active
        else:
            wb = Workbook()
            ws = wb.active
            ws.append(["입력시간", "전체사진", "줄1사진", "줄2사진", "줄1 제품", "줄2 제품", "브랜드", "카테고리"])

        row_num = ws.max_row + 1
        ws.cell(row=row_num, column=1, value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        ws.cell(row=row_num, column=5, value=line1)
        ws.cell(row=row_num, column=6, value=line2)
        ws.cell(row=row_num, column=7, value=brand)
        ws.cell(row=row_num, column=8, value=category)

        # 이미지 삽입 (크기: 약 4cm x 3cm → 픽셀 150 x 113)
        def insert_image(path, col_letter):
            img = XLImage(path)
            img.width, img.height = 150, 113
            ws.add_image(img, f"{col_letter}{row_num}")

        insert_image(full_path, "B")
        insert_image(line1_path, "C")
        insert_image(line2_path, "D")

        wb.save(EXCEL_PATH)
        st.success("✅ 입력이 저장되었습니다! 감사합니다 🙌")
    else:
        st.warning("⚠️ 모든 사진을 업로드해주세요.")
