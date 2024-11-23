from base64 import b64decode
from django.http import HttpRequest
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from receipt_scanner.api import api_scan
from receipt_scanner.ocr_space import ReceiptSummary
import io

from finanze import logger

class ScanReceipt(APIView):

    def post(self, request):
        # the body is actually the whole image, b64-encoded
        b64image = request.data.get("base64image")
        if not b64image:
            return Response({
                "error": "Invalid input"
            }, status=status.HTTP_400_BAD_REQUEST)
        img_bytes = b64decode(b64image)
        try:
            img_buf = io.BytesIO(img_bytes)
            restext = api_scan(img_buf)
            summary = ReceiptSummary.fromOCRSpaceJsonResponse(restext)
            if summary.total_guess() != ReceiptSummary.TOTAL_GUESS_NOT_AVALABLE_STRING:
                return Response({
                    "description": summary.vendor,
                    "date": summary.date,
                    "abs_amount": summary.total_guess()
                })
            else:
                return Response({
                    "warning": "Could not extract receipt data",
                })
        except Exception as ex:
            logger.error(f"receipt_scanner.api_scan failed with error: {str(ex)}")
            return Response({"error": "Image scan failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)