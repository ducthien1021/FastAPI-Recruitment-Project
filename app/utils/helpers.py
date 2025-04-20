import hashlib

def hash_password(password: str) -> str:
    """Hash password dùng SHA-256 (không dùng salt)"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password

def response(data=None, message="Thành công", code=200, status="Success"):
    return {
        "Code": code,
        "Status": status,
        "Message": message,
        "Data": data,
    }