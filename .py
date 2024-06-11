import base64
import zlib

# The session data you have
session_data = ".eJxVjDEOwjAMRe-SGUVpamKHkZ0zRHYcSAG1UtNOiLtDpQ6w_vfef5nE61LT2sqcBjUn483hdxPOjzJuQO883iabp3GZB7GbYnfa7GXS8jzv7t9B5Va_NXnADBGuJIE7BqGA0YF24ASdOwoVjxByDp4VIyIU0r7PhNI7UmfeH78fNvA:1s6wHB:cDn4W4QSvg6dDHgCelHnLF42oaKkSttPsyuRXMzF4JY"

# Extract the base64 part of the session data
base64_part = session_data.split(":")[1]

# Fix padding by adding '=' characters to make the length a multiple of 4
missing_padding = 4 - len(base64_part) % 4
if missing_padding:
    base64_part += '=' * missing_padding

# Decode the base64 string
try:
    decoded_data = base64.b64decode(base64_part)
    print("Base64 decoded successfully")
except base64.binascii.Error as e:
    print(f"Error decoding base64: {e}")

# Try to decompress the data
try:
    decompressed_data = zlib.decompress(decoded_data)
    print("Decompressed successfully")
except zlib.error as e:
    decompressed_data = decoded_data
    print(f"Data is not compressed or could not be decompressed: {e}")

# Print the first 1000 bytes for inspection
print(decompressed_data[:1000])
