import os

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from django.contrib.auth import get_user

from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.authtoken.serializers import AuthTokenSerializer
from knox.views import LoginView as KnoxLoginView

from finanze.permissions import IsOwnerOrDeny, IsAuthenticatedSelfUser


class TokenLoginView(KnoxLoginView):
    """Issue a Knox token from username/password in the request body.

    Same request format as DRF's obtain_auth_token, so clients only need to
    read the extra `expiry` field. Each login creates a separate token
    (one per device), stored hashed and expiring after REST_KNOX TOKEN_TTL.
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        request.user = serializer.validated_data['user']
        return super().post(request, format=format)


import re
from . import logger
from base64 import b64decode
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from receipt_scanner.api import api_scan
from receipt_scanner.ocr_space import ReceiptSummary
from rest_framework.permissions import IsAdminUser
from finanze.permissions import IsOwnerOrDeny, IsAuthenticatedSelfUser
from finanze.serializers import UserSerializer

import io


class InstanceInfo(APIView):
    """Public description of this instance, read by the frontend at startup.

    `features` tells which optional features have the external service key
    they need, so the UI can disable them with an explanation instead of
    failing on use. On a demo instance `demo_credentials` lets the login
    page show (and prefill) the shared demo account.
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        info = {
            "demo": settings.DEMO_MODE,
            "features": {
                "voice": bool(os.environ.get("OPENAI_API_KEY")),
            },
        }
        if settings.DEMO_MODE:
            info["demo_credentials"] = {
                "username": os.environ.get("DEMO_USERNAME", "demo"),
                "password": os.environ.get("DEMO_PASSWORD", "demo"),
            }
        return Response(info)


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


@login_required
def change_password(request) -> str:
    min_length = 8
    regexRequirements = [
        ('[@-_!#$%^&*()<>?/\|}{~:]', "special chars"),
        ('[0-9]', "digits"),
        ('[a-z]', "lowercase"),
        ('[A-Z]', "uppercase"),
    ]
    params = request.POST
    user: User = get_user(request)
    if user.check_password(params.get('old_password')) is False:
        return "old_password"
    np1 = params.get('new_password1')
    np2 = params.get('new_password2')
    if np1 != np2:
        logger.debug("[change_password] Verification failed: match")
        return "new_password2"
    if len(np1) < min_length:
        logger.debug("[change_password] Verification failed: length")
        return "new_password1"
    for regitem in regexRequirements:
        reg = regitem[0]
        type = regitem[1]
        pat = re.compile(reg)
        match = pat.search(np1)
        if not match:
            logger.debug("[change_password] Verification failed: %s" % type)
            return "new_password1"
    user.set_password(np1)
    user.save()
    return None


@login_required
def update_parameters(request) -> tuple:
    accepted_params = ['username', 'email']
    params = request.POST
    user: User = get_user(request)
    for ap in accepted_params:
        param = params.get(ap)
        if param:
            logger.debug("[update_parameters] Updating %s" % ap)
            user.__setattr__(ap, param)
            user.save()
            return None

class UserList(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    queryset = User.objects.all()
    serializer_class = UserSerializer

@login_required
def profile(request):
    if request.method == 'POST':
        if request.path.find('password-change') > 0:
            changed = change_password(request)
            if changed is None:
                return JsonResponse({})
            else:
                return JsonResponse({"error": [changed]})
        else: # other non-password parameters
            updated = update_parameters(request)
            if updated is None:
                return JsonResponse({})
            else:
                return JsonResponse({"error": {updated[0]: updated[1]}})
    else:
        return render(request, 'profile.html')

class UserList(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
    permission_classes = [IsAdminUser|IsAuthenticatedSelfUser]
    queryset = User.objects.all()
    serializer_class = UserSerializer


class LoggedInUserDetail(UserList):
    permission_classes = [IsAdminUser|IsAuthenticatedSelfUser]
    
    def get(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter(id=request.user.id)
        return super().get(request, *args, **kwargs)


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