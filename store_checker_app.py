import streamlit as st
import os
from datetime import datetime
from PIL import Image
from io import BytesIO
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import tempfile

# ⬇️ 구글 인증 설정
scope = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets'
]

# 서비스 계정 시크릿 불러오기 (secrets.toml 에 저장한 값)
credentials = ServiceAccountCredentials.from_json_keyfile_dict(
    st.secrets["gdrive_credentials"], scope
)

drive_auth = GoogleAuth()
drive_auth.credentials = credentials
drive = GoogleDrive(drive_auth)

gc = gspread.authorize(credentials)

# 📄 구글 시트 ID
SHEET_ID = "1ZpWTwJUjEWnMfQK7AICXANFV9BMSo_6JsZhVsatjVdM"
SHEET_NAME = "시트1"
worksheet = gc.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

# 📁 구글 드라이브 폴더 ID
FOLDER_ID = "1rrrt-OmAYA08FMmyw7qO2HApOgyC24LY"

st.title("📸 매장 진열 사진 등록 (Google 연동)")

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

# 업로드 함수
def upload_photo(photo_file, filename):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp.write(photo_file.getbuffer())
        gfile = drive.CreateFile({'title': filename, 'parents': [{'id': FOLDER_ID}]})
        gfile.SetContentFile(tmp.name)
        gfile.Upload()
        return gfile['alternateLink']

if st.button("제출하기"):
    if full_photo and line1_photo and line2_photo:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 📤 사진 업로드
        link_full = upload_photo(full_photo, f"full_{now}.jpg")
        link_line1 = upload_photo(line1_photo, f"line1_{now}.jpg")
        link_line2 = upload_photo(line2_photo, f"line2_{now}.jpg")

        # 📊 구글 시트에 정보 입력
        worksheet.append_row([
            now, link_full, link_line1, link_line2,
            line1, line2, brand, category
        ])

        st.success("✅ 제출 완료! 구글 드라이브와 시트에 업로드되었습니다.")
    else:
        st.warning("⚠️ 모든 사진을 업로드해주세요.")

