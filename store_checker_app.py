import streamlit as st
import pandas as pd
from openpyxl import load_workbook, Workbook
from openpyxl.drawing.image import Image as XLImage
from PIL import Image
import os
from datetime import datetime
import json

# ⬇️ 구글 드라이브 업로드용 추가
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials

# 파일 저장 경로
if not os.path.exists("photos"):
    os.makedirs("photos")
if not os.path.exists("output"):
    os.makedirs("output")

EXCEL_PATH = "output/store_checker_data.xlsx"

# ✅ 드라이브 업로드 함수
def upload_to_drive(local_path, file_name):
    scope = ['https://www.googleapis.com/auth/drive']

    # 👇 시크릿에 저장된 gdrive_credentials 불러오기
    json_key = json.loads(st.secrets["gdrive_credentials"])
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(json_key, scope)

    gauth = GoogleAuth()
    gauth.credentials = credentials
    drive = GoogleDrive(gauth)

    folder_id = '1rrrt-OmAYA08FMmyw7qO2HApOgyC24LY'  # ← 사용자에 따라 변경 필요

    # 기존 동일 파일 삭제
    file_list = drive.ListFile({'q': f"title='{file_name}' and '{folder_id}' in parents and trashed=false"}).GetList()
    for f in file_list:
        f.Delete()

    # 새로 업로드
    f = drive.CreateFile({'title': file_name, 'parents': [{'id': folder_id}]})
    f.SetContentFile(local_path)
    f.Upload()

# 브랜드/카테고리 선택
brands = ["테팔", "필립스", "락앤락", "도루코", "기타"]
categories = ["주방", "생활용품", "가전", "세제", "기타"]

st.title("매장 진열 사진 입력 앱")

# 사진 입력
col1, col2, col3 = st.columns(3)
with col1:
    full_photo = st.file_uploader("전체 진열사진", type=["jpg", "jpeg", "png"], key="full")
with col2:
    line1_photo = st.file_uploader("1번줄 사진", type=["jpg", "jpeg", "png"], key="line1")
with col3:
    line2_photo = st.file_uploader("2번줄 사진", type=["jpg", "jpeg", "png"], key="line2")

# 정보 입력
line1 = st.text_input("1번 줄 제품명")
line2 = st.text_input("2번 줄 제품명")
brand = st.selectbox("브랜드 선택", brands)
category = st.selectbox("카테고리 선택", categories)

# 저장 버튼
if st.button("제출하기"):
    if full_photo and line1_photo and line2_photo:
        now = datetime.now().strftime("%Y%m%d_%H%M%S")

        full_path = f"photos/full_{now}.jpg"
        line1_path = f"photos/line1_{now}.jpg"
        line2_path = f"photos/line2_{now}.jpg"
        with open(full_path, "wb") as f:
            f.write(full_photo.getbuffer())
        with open(line1_path, "wb") as f:
            f.write(line1_photo.getbuffer())
        with open(line2_path, "wb") as f:
            f.write(line2_photo.getbuffer())

        # 엑셀 열기/만들기
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

        def insert_image(path, col_letter):
            img = XLImage(path)
            img.width, img.height = 150, 113
            ws.add_image(img, f"{col_letter}{row_num}")

        insert_image(full_path, "B")
        insert_image(line1_path, "C")
        insert_image(line2_path, "D")

        wb.save(EXCEL_PATH)

        try:
            upload_to_drive(EXCEL_PATH, "store_checker_data.xlsx")
            st.success("✅ 저장 및 드라이브 업로드 완료!")
        except Exception as e:
            st.error(f"⚠️ 드라이브 업로드 실패: {e}")
    else:
        st.warning("⚠️ 모든 사진을 업로드해주세요.")

