"""
File: utils.py
Mô tả:
    Chứa các hàm tiện ích dùng để xử lý tên file và định dạng thời gian.
"""

import re
import unicodedata

def sanitize_filename(filename):
    """
    Chuyển đổi tên file:
      - Loại bỏ dấu tiếng Việt.
      - Loại bỏ khoảng trắng và các ký tự không hợp lệ.
    
    :param filename: Tên file cần chuyển đổi.
    :return: Tên file đã được chuẩn hóa.
    """
    filename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore').decode('ASCII')
    filename = re.sub(r'[^\w\-\.]', '_', filename)
    return filename

def format_time(seconds):
    """
    Chuyển số giây thành định dạng thời gian hh:mm:ss hoặc mm:ss (nếu video ngắn).
    
    :param seconds: Số giây cần chuyển đổi.
    :return: Chuỗi thời gian định dạng.
    """
    seconds = int(seconds)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    else:
        return f"{m:02d}:{s:02d}"

def parse_time(time_str):
    """
    Chuyển chuỗi thời gian (có thể ở dạng ss, mm:ss, hoặc hh:mm:ss) thành số giây.
    
    :param time_str: Chuỗi thời gian cần chuyển đổi.
    :return: Số giây tương ứng.
    :raises ValueError: Nếu định dạng thời gian không hợp lệ.
    """
    time_str = time_str.strip()
    parts = time_str.split(':')
    if len(parts) == 1:
        return float(parts[0])
    elif len(parts) == 2:
        minutes, seconds = parts
        return int(minutes) * 60 + float(seconds)
    elif len(parts) == 3:
        hours, minutes, seconds = parts
        return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    else:
        raise ValueError("Định dạng thời gian không hợp lệ")
