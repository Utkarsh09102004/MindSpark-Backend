from django.urls import re_path
from .consumers import QuizSessionConsumer

websocket_urlpatterns = [
    re_path(r'ws/quizroom/(?P<unique_code>\w+)/$', QuizSessionConsumer.as_asgi()),
]
