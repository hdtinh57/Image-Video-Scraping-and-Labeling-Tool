# utils.py
import re
import unicodedata

def sanitize_filename(filename):
    """
    Chuyển đổi tên file: loại bỏ dấu tiếng Việt, khoảng trắng và các ký tự không hợp lệ.
    """
    filename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore').decode('ASCII')
    filename = re.sub(r'[^\w\-\.]', '_', filename)
    return filename

def format_time(seconds):
    """Chuyển số giây thành định dạng hh:mm:ss (hoặc mm:ss nếu video ngắn)."""
    seconds = int(seconds)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    else:
        return f"{m:02d}:{s:02d}"

def parse_time(time_str):
    """Chuyển chuỗi thời gian (ss, mm:ss, hoặc hh:mm:ss) thành số giây."""
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
