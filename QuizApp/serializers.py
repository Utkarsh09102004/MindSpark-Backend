from rest_framework import serializers
from .models import Session, Question

class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = ['start_time', 'max_participants']  # Only expose these fields to the frontend

    def create(self, validated_data):
        request = self.context.get('request')
        quiz_master = request.user  # Assuming the request has the user set as the quiz_master


        # Create the session instance
        session = Session.objects.create(
            start_time=validated_data['start_time'],
            max_participants=validated_data['max_participants'],
            quiz_master=quiz_master,
            is_active=True
        )
        return session


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        exclude = ['session']  # Exclude the 'sessions' field

    def create(self, validated_data):
        session = self.context['session']
        validated_data['session'] = session
        return super().create(validated_data)