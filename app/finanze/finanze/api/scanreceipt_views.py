from base64 import b64decode
from django.http import HttpRequest

def scan_receipt(request: HttpRequest):
    # the body is actually the whole image, b64-encoded
   img_bytes = b64decode(request.body)