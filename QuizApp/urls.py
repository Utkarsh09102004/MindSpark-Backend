from django.urls import path

from .viewsDirectory.sessionViews import *
from .viewsDirectory.questionViews import *

urlpatterns = [
    path("create-session/", SessionCreateView.as_view(), name="create-session"),
    path('<str:unique_code>/create-question/', CreateQuestionView.as_view(), name='create-question'),
    path('<str:unique_code>/find-question/', QuestionsBySessionView.as_view(), name='find-question'),
    path('<str:unique_code>/update-questions/', UpdateQuestionView.as_view(), name='update_question'),
    path('delete-question/<int:pk>/', DeleteQuestionView.as_view(), name='delete-question')
]