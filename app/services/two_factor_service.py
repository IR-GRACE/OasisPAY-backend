import pyotp
import qrcode
import io
import base64
from fastapi import HTTPException

class TwoFactorService:
    @staticmethod
    def generate_secret():
        return pyotp.random_base32()
    
    @staticmethod
    def get_qr_code(secret, email):
        totp = pyotp.TOTP(secret)
        uri = totp.provisioning_uri(name=email, issuer_name="OasisPay")
        
        qr = qrcode.QRCode(box_size=10, border=4)
        qr.add_data(uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        
        return base64.b64encode(buffer.getvalue()).decode()
    
    @staticmethod
    def verify_code(secret, code):
        totp = pyotp.TOTP(secret)
        return totp.verify(code)
