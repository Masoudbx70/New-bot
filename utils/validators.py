import re

def validate_phone(phone):
    pattern = r'^(\+98|0)?9\d{9}$'
    return re.match(pattern, phone) is not None

def validate_name(name):
    # نام باید فقط حاوی حروف فارسی یا انگلیسی و فاصله باشد
    pattern = r'^[\u0600-\u06FFa-zA-Z\s]+$'
    return re.match(pattern, name) is not None