import streamlit as st
from tinydb import TinyDB, Query
import bcrypt
from utils import check_and_update_date_column

DB_PATH = 'db/user_db.json'
db = TinyDB(DB_PATH)
User = Query()

def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

def login_user(username, password):
    user_record = db.search(User.username == username)
    if user_record:
        stored_hash = user_record[0]['password'].encode('latin-1')
        if check_password(password, stored_hash):
            return True, user_record[0]
    return False, None

st.set_page_config(layout="centered")
st.title("เข้าสู่ระบบ")

if st.session_state.get('logged_in', False):
    st.switch_page("pages/qr_manager.py") 

with st.form("login_form"):
    username = st.text_input("ชื่อผู้ใช้")
    password = st.text_input("รหัสผ่าน", type="password")
    login_button = st.form_submit_button("เข้าสู่ระบบ")

if login_button:
    if not username or not password:
        st.error("โปรดกรอกทั้งชื่อผู้ใช้และรหัสผ่าน")
    else:
        success, user_data = login_user(username, password)
        
        if success:
            st.session_state.logged_in = True
            st.session_state.username = user_data['username']
            st.session_state.full_name = user_data['full_name']
            
            st.success(f"เข้าสู่ระบบสำเร็จ! ยินดีต้อนรับ, {user_data['full_name']}!")
            
            # --- Check Google Sheet Date Column ---
            with st.spinner("กำลังตรวจสอบข้อมูล..."):
                try:
                    check_and_update_date_column()
                except Exception as e:
                    st.warning(f"ไม่สามารถเชื่อมต่อ Google Sheet ได้: {e}")
            # ------------------------------------------------
            
            st.info("กำลังนำทางไปยังหน้าจัดการ...")
            st.switch_page("pages/qr_manager.py")
        else:
            st.error("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")

st.markdown("---")
st.write("ยังไม่มีบัญชี?")
if st.button("ไปที่หน้าสมัครใช้งาน"):
    st.switch_page("pages/register.py")