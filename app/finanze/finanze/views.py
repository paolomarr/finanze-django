from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.utils.translation import gettext as _
from django.contrib.auth import get_user
import re
from . import logger

def index(request):
    if request.user.is_authenticated:
        return render(request,
                      'landing.html')
    else:
        return redirect('/login/')


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