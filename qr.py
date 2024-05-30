import time
import pyotp
import qrcode

key = "Prospace"

uri = pyotp.totp.TOTP(key).provisioning_uri(name="pspace", issuer_name="ahil")

print(uri)
qrcode.make(uri).save("totp.png")