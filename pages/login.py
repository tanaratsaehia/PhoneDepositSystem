# pages/login.py
import streamlit as st
from tinydb import TinyDB, Query
import bcrypt

DB_PATH = 'db/user_db.json'
db = TinyDB(DB_PATH)
User = Query()

def check_password(password, hashed_password):
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

def login_user(username, password):
    """
    Query the database and verify the password.
    Returns: True/False and the user data (or None).
    """
    user_record = db.search(User.username == username)
    if user_record:
        # Assuming the stored hash is stored as a string that can be decoded to bytes
        # Using 'latin-1' or 'iso-8859-1' is common for simple string/byte conversion in Python for data that is essentially bytes
        stored_hash = user_record[0]['password'].encode('latin-1') 
        if check_password(password, stored_hash):
            return True, user_record[0]
    return False, None

st.set_page_config(
    layout="centered"
)
# --- Streamlit Login Page Layout ---
st.title("เข้าสู่ระบบ") # Changed "Login" to "เข้าสู่ระบบ"

if st.session_state.get('logged_in', False):
    st.switch_page("pages/qr_manager.py")

with st.form("login_form"):
    username = st.text_input("ชื่อผู้ใช้") # Changed "Username" to "ชื่อผู้ใช้"
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
            st.info("กำลังนำทางไปยังหน้าหลัก...") 
            st.switch_page("pages/qr_manager.py")
        else:
            
            st.error("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง") 

st.markdown("---")
st.write("ยังไม่มีบัญชี?")
if st.button("ไปที่หน้าสมัครใช้งาน"): 
    st.switch_page("pages/register.py")