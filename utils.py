# utils.py
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import streamlit as st

SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS_FILE = 'service_account.json' 
SHEET_NAME = 'MockupData for PhoneDepositSystem'

def get_sheet():
    """เชื่อมต่อกับ Google Sheet และคืนค่า Worksheet แรก"""
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPE)
        client = gspread.authorize(creds)
        sheet = client.open(SHEET_NAME).sheet1
        return sheet
    except Exception as e:
        st.error(f"ไม่สามารถเชื่อมต่อ Google Sheets ได้: {e}")
        return None

def get_thai_date():
    """คืนค่าวันที่ปัจจุบันในรูปแบบ dd/mm/yyyy (พ.ศ.)"""
    now = datetime.now()
    thai_year = now.year + 543
    return now.strftime(f"%d/%m/{thai_year}")

def add_user_to_sheet(full_name):
    """เพิ่มผู้ใช้ใหม่ลงใน Sheet (ใช้ใน register.py)"""
    sheet = get_sheet()
    if sheet:
        data = sheet.get_all_values()
        if len(data) <= 1:
            new_id = 1
        else:
            try:
                new_id = int(data[-1][0]) + 1
            except:
                new_id = len(data)
        
        # เตรียมข้อมูลแถวใหม่: [ID, ชื่อ, "ยังไม่ฝาก", "ยังไม่ฝาก", ...]
        # เติมค่า default สำหรับคอลัมน์วันที่ที่มีอยู่แล้ว
        num_cols = len(data[0]) if data else 2
        row_data = [new_id, full_name] + ["ยังไม่ฝาก"] * (num_cols - 2)
        
        sheet.append_row(row_data)

def check_and_update_date_column():
    """ตรวจสอบว่ามีคอลัมน์วันที่ปัจจุบันหรือยัง ถ้าไม่มีให้สร้างใหม่ (ใช้ใน login.py)"""
    sheet = get_sheet()
    if sheet:
        headers = sheet.row_values(1)
        current_date = get_thai_date()
        
        if current_date not in headers:
            # ถ้ายังไม่มีวันที่นี้ ให้เพิ่มคอลัมน์ใหม่
            # gspread append_col อาจจะซับซ้อน ใช้ update cell ธรรมดา
            new_col_index = len(headers) + 1
            
            # อัปเดต Header
            sheet.update_cell(1, new_col_index, current_date)
            
            # อัปเดตค่า "ยังไม่ฝาก" ให้กับทุก User ที่มีอยู่
            user_rows = len(sheet.col_values(1)) # จำนวนแถวทั้งหมด
            if user_rows > 1:
                # สร้าง list ของค่าที่จะเติม
                updates = [["ยังไม่ฝาก"]] * (user_rows - 1)
                # แปลง index เป็นตัวอักษร A, B, C... เพื่อระบุ range (เช่น C2:C10)
                # เพื่อความง่าย ใช้ update_cell วนลูป (ถ้า user เยอะควรใช้ batch_update แต่เบื้องต้นใช้วิธีนี้ก่อน)
                for i in range(2, user_rows + 1):
                    sheet.update_cell(i, new_col_index, "ยังไม่ฝาก")

def process_deposit(qr_text):
    """ประมวลผลการฝากเมื่อ Admin สแกน"""
    sheet = get_sheet()
    if not sheet:
        return False, "เชื่อมต่อ Database ไม่ได้"

    current_date = get_thai_date()
    headers = sheet.row_values(1)
    
    if current_date not in headers:
        return False, f"ไม่พบคอลัมน์วันที่ {current_date} (ระบบอาจยังไม่อัปเดตตอน Login)"
    
    date_col_index = headers.index(current_date) + 1
    name_col_index = 2 # "ชื่อ" อยู่ที่ Column 2 (B)
    
    # ค้นหาแถวที่มีชื่อตรงกับ QR Code
    try:
        cell = sheet.find(qr_text, in_column=name_col_index)
        if cell:
            # อัปเดตสถานะเป็น "ฝากแล้ว"
            sheet.update_cell(cell.row, date_col_index, "ฝากแล้ว")
            return True, f"บันทึกการฝากของ {qr_text} สำเร็จ!"
        else:
            return False, f"ไม่พบชื่อ '{qr_text}' ในระบบ"
    except Exception as e:
        return False, f"เกิดข้อผิดพลาด: {e}"