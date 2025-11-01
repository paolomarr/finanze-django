# voice_movements/urls.py
from django.urls import path
from .views import VoiceMovementView, TextMovementView
from django.conf import settings

app_name = 'voice_movements'

urlpatterns = [
    path('voice/', VoiceMovementView.as_view(), name='voice_movement'),
]
if settings.DEBUG:
    urlpatterns.append(path('text/', TextMovementView.as_view(), name='text_movement'))