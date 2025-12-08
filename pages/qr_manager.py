import streamlit as st
import qrcode
from PIL import Image
import io
import cv2
import numpy as np
from utils import process_deposit

st.set_page_config(page_title="ระบบฝากโทรศัพท์", layout="centered")

# ตรวจสอบการ Login
if not st.session_state.get('logged_in', False):
    st.error("กรุณาเข้าสู่ระบบก่อน")
    st.switch_page("pages/login.py")

# ดึงข้อมูล user
username = st.session_state.username
full_name = st.session_state.full_name

# --- ส่วนของ Logout Logic ---
def logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.full_name = None
    st.switch_page("pages/login.py")

# ==========================================
# USER WITH USERNAME == "admin"
# ==========================================
if username == "admin":
    # Header layout
    col1, col2, col3 = st.columns([3, 1.5, 1])
    with col1:
        st.subheader("สวัสดีผู้ดูแลระบบฝากโทรศัพท์")
    with col2:
        if st.button("🔍 ค้นหาข้อมูล"):
            # st.toast("ฟีเจอร์ค้นหากำลังพัฒนา") 
            st.switch_page("pages/search.py")
    with col3:
        if st.button("ออกจากระบบ"):
            logout()
    
    st.divider()
    
    # Make user event for take a picture (Using Camera Input)
    st.write("### 📷 สแกน QR Code เพื่อรับฝาก")
    
    # ใช้ camera_input ของ Streamlit
    img_file_buffer = st.camera_input("ถ่ายภาพ QR Code ของนักเรียน")
    
    if img_file_buffer is not None:
        # แปลงรูปภาพเพื่อใช้กับ OpenCV
        bytes_data = img_file_buffer.getvalue()
        cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
        
        # ตรวจจับ QR Code
        detector = cv2.QRCodeDetector()
        data, bbox, _ = detector.detectAndDecode(cv2_img)
        
        if data:
            # Update Google Sheet and Show Message
            with st.spinner(f"กำลังประมวลผลสำหรับ: {data}..."):
                success, message = process_deposit(data)
                
            if success:
                st.success(message)
                st.info("ถ่ายภาพใหม่เพื่อสแกนคนถัดไป")
            else:
                st.error(message)
        else:
            st.warning("ไม่พบ QR Code ในภาพ กรุณาถ่ายใหม่อีกครั้งให้ชัดเจน")

# ==========================================
# NORMAL USER
# ==========================================
else:
    # Header Layout
    col1, col2 = st.columns([4, 1])
    with col1:
        st.subheader(f"สวัสดี {full_name}")
    with col2:
        if st.button("ออกจากระบบ"):
            logout()
            
    st.divider()
    
    # Show QR Code
    st.write("### QR Code ของฉัน")
    
    # Generate QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    # ใส่ข้อมูล full_name ลงใน QR
    qr.add_data(full_name)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert PIL image to displayable format in Streamlit
    # แสดงผลตรงกลาง
    col_img1, col_img2, col_img3 = st.columns([1, 2, 1])
    with col_img2:
        st.image(img.get_image(), caption=f"ชื่อ: {full_name}", width=300)
        st.info("แสดง QR Code นี้ให้ผู้ดูแลระบบสแกนเพื่อฝากโทรศัพท์")