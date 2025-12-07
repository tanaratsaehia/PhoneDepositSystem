import streamlit as st
from tinydb import TinyDB, Query
import bcrypt
from utils import add_user_to_sheet
import time

DB_PATH = 'db/user_db.json'
db = TinyDB(DB_PATH)
User = Query()

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('latin-1')

def register_user(username, full_name, password):
    if db.search(User.username == username):
        return False
    
    hashed_password = hash_password(password)
    
    db.insert({
        'username': username,
        'full_name': full_name,
        'password': hashed_password
    })
    
    # --- ACTION 1: Add to Google Sheet if not Admin ---
    if username != "admin":
        try:
            add_user_to_sheet(full_name)
        except Exception as e:
            print(f"Failed to add to sheet: {e}")
            
    return True

# --- Streamlit Register Page Layout ---
st.title("📝 ลงทะเบียนบัญชีใหม่")

if st.session_state.get('logged_in', False):
    st.warning("คุณเข้าสู่ระบบอยู่แล้ว กรุณาออกจากระบบก่อนเพื่อลงทะเบียนบัญชีใหม่")
    st.stop()

with st.form("register_form"):
    username = st.text_input("ชื่อผู้ใช้", help="ใช้สำหรับเข้าสู่ระบบ")
    full_name = st.text_input("ชื่อ-นามสกุล", help="ใช้สำหรับแสดงชื่อในการบันทึกข้อมูล/ประวัติ")
    password = st.text_input("รหัสผ่าน", type="password")
    confirm_password = st.text_input("ยืนยันรหัสผ่าน", type="password")
    register_button = st.form_submit_button("ลงทะเบียน")

if register_button:
    if not username or not full_name or not password or not confirm_password:
        st.error("กรุณากรอกข้อมูลในช่องที่จำเป็นทั้งหมด")
    elif password != confirm_password:
        st.error("รหัสผ่านไม่ตรงกัน!")
    elif len(password) < 6:
        st.error("รหัสผ่านต้องมีความยาวอย่างน้อย 6 ตัวอักษร")
    else:
        # เรียกใช้ฟังก์ชันที่มีการเพิ่มลง Sheet แล้ว
        st.info("กำลังลงทะเบียน...")
        if register_user(username, full_name, password):
            st.success("ลงทะเบียนสำเร็จ! และเพิ่มข้อมูลลงฐานข้อมูลเรียบร้อยแล้ว")
            st.info("กำลังนำทางไปยังหน้าเข้าสู่ระบบ...")
            time.sleep(1)
            st.switch_page("pages/login.py")
        else:
            st.error("การลงทะเบียนล้มเหลว ชื่อผู้ใช้นี้มีอยู่แล้ว")

st.markdown("---")
st.write("มีบัญชีอยู่แล้ว?")
if st.button("ไปที่หน้าเข้าสู่ระบบ"):
    st.switch_page("pages/login.py")