# pages/register.py
import streamlit as st
from tinydb import TinyDB, Query
import bcrypt
import os

# --- Setup Database and Hashing ---
DB_PATH = 'db/user_db.json'
db = TinyDB(DB_PATH)
User = Query()

def hash_password(password):
    """Hash a password using bcrypt."""
    # generate a salt and hash the password
    # gensalt() generates a random salt
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('latin-1')

def register_user(username, full_name, password):
    """
    Check if username exists and register the new user.
    Returns: True on success, False otherwise.
    """
    if db.search(User.username == username):
        return False # Username already exists
    
    hashed_password = hash_password(password)
    
    db.insert({
        'username': username,
        'full_name': full_name,
        'password': hashed_password # Store the hash
    })
    return True

# --- Streamlit Register Page Layout ---
st.title("📝 ลงทะเบียนบัญชีใหม่") # Changed "Register New Account" to "ลงทะเบียนบัญชีใหม่"

if st.session_state.get('logged_in', False):
    # Changed warning message
    st.warning("คุณเข้าสู่ระบบอยู่แล้ว กรุณาออกจากระบบก่อนเพื่อลงทะเบียนบัญชีใหม่") 
    st.stop()

with st.form("register_form"):
    # 1. Username
    # Changed "Username" to "ชื่อผู้ใช้"
    username = st.text_input("ชื่อผู้ใช้", help="ใช้สำหรับเข้าสู่ระบบ")
    
    # 2. Full Name
    # Changed "Full Name" to "ชื่อ-นามสกุล"
    full_name = st.text_input("ชื่อ-นามสกุล", help="ใช้สำหรับตรวจสอบการฝากโทรศัพท์")
    
    # 3. Password
    # Changed "Password" to "รหัสผ่าน"
    password = st.text_input("รหัสผ่าน", type="password")
    # Changed "Confirm Password" to "ยืนยันรหัสผ่าน"
    confirm_password = st.text_input("ยืนยันรหัสผ่าน", type="password")
    
    # Changed "Register" to "ลงทะเบียน"
    register_button = st.form_submit_button("ลงทะเบียน")

if register_button:
    if not username or not full_name or not password or not confirm_password:
        # Changed error message
        st.error("กรุณากรอกข้อมูลในช่องที่จำเป็นทั้งหมด") 
    elif password != confirm_password:
        # Changed error message
        st.error("รหัสผ่านไม่ตรงกัน!")
    elif len(password) < 6:
        # Changed error message
        st.error("รหัสผ่านต้องมีความยาวอย่างน้อย 6 ตัวอักษร")
    else:
        if register_user(username, full_name, password):
            # Changed success message
            st.success("ลงทะเบียนสำเร็จ! ตอนนี้คุณสามารถเข้าสู่ระบบได้แล้ว")
            # Auto-navigate to login page
            # Changed info message
            st.info("กำลังนำทางไปยังหน้าเข้าสู่ระบบ...")
            st.switch_page("pages/login.py")
        else:
            # Changed error message
            st.error("การลงทะเบียนล้มเหลว ชื่อผู้ใช้นี้มีอยู่แล้ว") 

st.markdown("---")
# Changed "Already have an account?" to Thai
st.write("มีบัญชีอยู่แล้ว?")
# Changed "Go to Login" to "ไปที่หน้าเข้าสู่ระบบ"
if st.button("ไปที่หน้าเข้าสู่ระบบ"):
    st.switch_page("pages/login.py")