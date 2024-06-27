from django.urls import path

from .views import *

urlpatterns = [
    path("create-session/", SessionCreateView.as_view(), name="create-session"),
    path('<str:unique_code>/create-question/', CreateQuestionView.as_view(), name='create-question')
]