
from rest_framework import generics


from ..serializers import *
from rest_framework.permissions import IsAuthenticated, AllowAny


class SessionCreateView(generics.CreateAPIView):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    permission_classes = [IsAuthenticated]