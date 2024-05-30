import time
import pyotp
import qrcode

key = "Prospace"

totp = pyotp.TOTP(key)

while True:
    print(totp.verify(input("Enter OTP: ")))