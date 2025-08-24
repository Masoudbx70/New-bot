import re

def validate_national_code(code):
    """اعتبارسنجی کد ملی ایران"""
    if not re.match(r'^\d{10}$', code):
        return False
    check = int(code[9])
    s = sum(int(code[i]) * (10 - i) for i in range(9)) % 11
    return (s < 2 and check == s) or (s >= 2 and check + s == 11)

def validate_email(email):
    """اعتبارسنجی ایمیل"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None