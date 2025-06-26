import streamlit as st
from supabase import create_client, Client
import uuid
from PIL import Image
from io import BytesIO

# ✅ Supabase 연결
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.title("🛒 제품 사진 + 데이터 입력 폼")

# 👉 사진 업로드
full_photo = st.file_uploader("전체 진열 사진", type=["png", "jpg", "jpeg"])
line1_photo = st.file_uploader("1번 줄 사진", type=["png", "jpg", "jpeg"])
line2_photo = st.file_uploader("2번 줄 사진", type=["png", "jpg", "jpeg"])

brand = st.selectbox("브랜드", ["락앤락", "테팔", "키친아트", "코렐", "필립스", "기타"])
category = st.selectbox("카테고리", ["믹서기", "프라이팬", "냄비", "밀폐용기", "전기포트", "기타"])

if st.button("저장"):
    with st.spinner("⏳ 저장 중입니다..."):
        photo_urls = {}
        for label, photo in zip(["full", "line1", "line2"], [full_photo, line1_photo, line2_photo]):
            if photo:
                img_bytes = photo.read()
                filename = f"{label}_{uuid.uuid4()}.png"
                supabase.storage.from_("product-images").upload(filename, img_bytes)
                public_url = supabase.storage.from_("product-images").get_public_url(filename)
                photo_urls[label] = public_url

        # ✅ 테이블에 저장
        supabase.table("product_photos").insert({
            "full_photo": photo_urls.get("full", ""),
            "line1_text": photo_urls.get("line1", ""),
            "line2_text": photo_urls.get("line2", ""),
            "brand": brand,
            "category": category,
        }).execute()

    st.success("✅ 저장 완료!")
