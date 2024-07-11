from rest_framework.permissions import BasePermission
from .models import Session, Question


class IsQuizMaster(BasePermission):
    def has_permission(self, request, view):
        if 'unique_code' in view.kwargs:
            # For CreateQuestionView
            unique_code = view.kwargs['unique_code']
            session = Session.objects.filter(unique_code=unique_code).first()
            if session and request.user == session.quiz_master:
                return True
        elif 'pk' in view.kwargs:
            # For UpdateQuestionView
            question_id = view.kwargs['pk']
            question = Question.objects.filter(pk=question_id).first()
            if question:
                session = question.session
                if session and request.user == session.quiz_master:
                    return True
        return False
