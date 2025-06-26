import streamlit as st
from supabase import create_client, Client
from PIL import Image
from io import BytesIO
import pandas as pd
import uuid
import base64
import openpyxl

# ✅ Supabase 연결
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.title("🛒 제품 사진 + 데이터 입력 폼")

# 📷 사진 입력
full_photo = st.file_uploader("전체 진열 사진", type=["png", "jpg", "jpeg"])
line1_photo = st.file_uploader("1번 줄 사진", type=["png", "jpg", "jpeg"])
line2_photo = st.file_uploader("2번 줄 사진", type=["png", "jpg", "jpeg"])

brand = st.selectbox("브랜드", ["락앤락", "테팔", "도루코", "기타"])
category = st.selectbox("카테고리", ["믹서기", "후라이팬", "냄비", "기타"])

if st.button("저장"):
    with st.spinner("사진 업로드 중..."):
        photo_urls = []
        for photo_file, label in zip([full_photo, line1_photo, line2_photo], ["full", "line1", "line2"]):
            if photo_file:
                img_bytes = photo_file.read()
                filename = f"{label}_{uuid.uuid4()}.jpg"
                supabase.storage.from_("product-images").upload(filename, img_bytes)
                public_url = supabase.storage.from_("product-images").get_public_url(filename)
                photo_urls.append(public_url)
            else:
                photo_urls.append("")

        # DB 저장
        supabase.table("product_photos").insert({
            "full_photo": photo_urls[0],
            "line1_text": photo_urls[1],
            "brand": brand,
            "category": category
        }).execute()

    st.success("📸 업로드 및 저장 완료!")
