FROM python:3.11-slim

WORKDIR /app

# نصب dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# کپی کردن کدهای برنامه
COPY . .

# اجرای برنامه
CMD ["python", "main.py"]
