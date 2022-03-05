from django.shortcuts import render, get_object_or_404


def index(request):
    if request.user.is_authenticated:
        return render(request,
                      'landing.html')
    else:
        get_object_or_404(None)
