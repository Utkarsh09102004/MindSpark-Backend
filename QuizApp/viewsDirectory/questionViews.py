from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from ..permissions import IsQuizMaster

from ..serializers import *
from rest_framework.permissions import IsAuthenticated, AllowAny




class CreateQuestionView(APIView):
    permission_classes = [IsAuthenticated, IsQuizMaster]

    def post(self, request, unique_code):
        session = get_object_or_404(Session, unique_code=unique_code)
        if request.user != session.quiz_master:
            return Response(
                {'error': f'You are not authorized to add questions to this session. You are {request.user.username}'},
                status=status.HTTP_403_FORBIDDEN
            )
        data = request.data
        if isinstance(data, list):
            serializer = QuestionSerializer(data=data, many=True, context={'session': session})
        else:
            serializer = QuestionSerializer(data=data, context={'session': session})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class QuestionsBySessionView(generics.ListAPIView):
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated, IsQuizMaster]

    def get(self, request, unique_code):
        session = get_object_or_404(Session, unique_code=unique_code)
        questions = Question.objects.filter(session=session)
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)


class UpdateQuestionView(APIView):
    permission_classes = [IsAuthenticated, IsQuizMaster]
    def put(self, request,unique_code):
        data = request.data
        if isinstance(data, list):
            response_data = []
            errors = []
            for question_data in data:
                question = get_object_or_404(Question, pk=question_data.get('id'))
                serializer = QuestionSerializer(question, data=question_data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    response_data.append(serializer.data)
                else:
                    errors.append(serializer.errors)
            if errors:
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(response_data, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid data format'}, status=status.HTTP_400_BAD_REQUEST)


class DeleteQuestionView(APIView):
    permission_classes = [IsAuthenticated, IsQuizMaster]

    def delete(self, request, pk):
        question = get_object_or_404(Question, pk=pk)
        question.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)