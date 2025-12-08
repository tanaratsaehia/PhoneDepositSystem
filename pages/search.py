import streamlit as st
import google.generativeai as genai
import pandas as pd
from utils import get_sheet
import os
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="ค้นหาข้อมูลฝากโทรศัพท์", layout="centered")

# --- Authentication Check (Admin Only) ---
if not st.session_state.get('logged_in', False):
    st.error("กรุณาเข้าสู่ระบบก่อน")
    st.switch_page("pages/login.py")

if st.session_state.username != "admin":
    st.error("หน้านี้สำหรับผู้ดูแลระบบเท่านั้น")
    st.stop()

# --- Setup Gemini API ---
api_key = os.getenv("GEMINI_API_KEY")

# --- Logout Logic ---
def logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.full_name = None
    st.switch_page("pages/login.py")

# --- Header Layout ---
col1, col2, col3 = st.columns([3, 1.5, 1])

with col1:
    st.subheader("สวัสดีผู้ดูแลระบบฝากโทรศัพท์")

with col2:
    if st.button("📸 สแกน QR Code"):
        st.switch_page("pages/qr_manager.py")

with col3:
    if st.button("ออกจากระบบ"):
        logout()

st.divider()

# --- Search Interface ---
st.write("### 🔍 ค้นหาข้อมูลด้วย AI")
st.caption("ถามคำถามเกี่ยวกับสถานะการฝากโทรศัพท์ เช่น 'วันนี้ใครยังไม่ฝากบ้าง', 'สมชาย ฝากหรือยัง'")

# Input สำหรับ API Key (กรณีไม่ได้ตั้งค่าใน Environment)
if not api_key:
    api_key = st.text_input("กรุณากรอก Gemini API Key", type="password")

query = st.text_area("พิมพ์คำถามของคุณที่นี่", height=100)
search_button = st.button("ค้นหาคำตอบ")

if search_button:
    if not api_key:
        st.error("กรุณาระบุ Gemini API Key")
    elif not query:
        st.warning("กรุณาพิมพ์คำถามก่อนค้นหา")
    else:
        with st.spinner("กำลังดึงข้อมูลล่าสุดและวิเคราะห์คำตอบ..."):
            # Fetch Latest Data from Google Sheet
            try:
                sheet = get_sheet()
                if sheet:
                    # ดึงข้อมูลทั้งหมดมาเป็น List of Lists
                    data = sheet.get_all_values()
                    
                    # แปลงเป็น DataFrame หรือ Text string เพื่อให้ AI อ่านรู้เรื่อง
                    df = pd.DataFrame(data[1:], columns=data[0])
                    data_context = df.to_csv(index=False)
                    
                    # Configure Gemini
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    
                    # Construct Prompt
                    system_instruction = """
คุณคือ AI ที่ช่วยตอบคำถามในระบบรับฝากโทรศัพท์โดยข้อมูลจะอ้างอิงจาก google sheet ที่ให้ค้นหาเท่านั้น
รูปแบบคำตอบให้ตอบเป็นข้อความปกติเท่านั้นให้ตัดส่วน markdown ออกทั้งหมด
หากได้รับคำถามที่นอกเหนือจากคำถามในระบบรับฝากโทรศัพท์ให้ตอบว่า  'ขออภัยไม่สามารถตอบคำถามที่ไม่เกี่ยวข้องกับระบบ'
**สำคัญ** การตอบกลับกำหนดขนาดให้ไม่เกิน 150 คำหากตอบจำนวนคำน้อยๆ จะดีมาก

คำถามเพื่อค้นหาข้อมูลคือ {user_input}
"""
                    full_prompt = f"""
{system_instruction.format(user_input=query)}

ข้อมูลอ้างอิงจาก Google Sheet (อัปเดตล่าสุด):
{data_context}
"""
                    # Generate Content
                    response = model.generate_content(full_prompt)
                    
                    # Display Result
                    st.success(f"ผลการค้นหา: {response.text}")
                else:
                    st.error("ไม่สามารถดึงข้อมูลจาก Google Sheet ได้")
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาด: {e}")