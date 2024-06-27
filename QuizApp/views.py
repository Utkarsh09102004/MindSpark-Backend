from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Session
from .serializers import *
from rest_framework.permissions import IsAuthenticated, AllowAny

# Create your views here.
class SessionCreateView(generics.CreateAPIView):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    permission_classes = [IsAuthenticated]


class CreateQuestionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, unique_code):
        session = get_object_or_404(Session, unique_code=unique_code)

        # Check if the current user is the quiz master of the session
        if request.user != session.quiz_master:
            return Response({'error': 'You are not authorized to add questions to this session.'},
                            status=status.HTTP_403_FORBIDDEN)

        # Deserialize the data
        data = request.data
        if isinstance(data, list):
            serializer = QuestionSerializer(data=data, many=True, context={'session': session})
        else:
            serializer = QuestionSerializer(data=data, context={'session': session})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


