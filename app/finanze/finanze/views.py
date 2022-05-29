from django.shortcuts import render, redirect


def index(request):
    if request.user.is_authenticated:
        return render(request,
                      'landing.html')
    else:
        return redirect('/login/')
