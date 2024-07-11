from rest_framework import serializers
from .models import Session, Question

class SessionSerializer(serializers.ModelSerializer):
    unique_code = serializers.CharField(read_only=True)  # Make the unique_code read-only

    class Meta:
        model = Session
        fields = ['name', 'start_time', 'max_participants', 'unique_code']  # Include unique_code in the fields

    def create(self, validated_data):
        request = self.context.get('request')
        quiz_master = request.user  # Assuming the request has the user set as the quiz_master

        # Create the session instance
        session = Session.objects.create(
            name=validated_data['name'],
            start_time=validated_data['start_time'],
            max_participants=validated_data['max_participants'],
            quiz_master=quiz_master,
            is_active=True
        )
        return session


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'  # Include all fields
        read_only_fields = ['session']  # Make session read-only

    def create(self, validated_data):
        session = self.context['session']
        validated_data['session'] = session
        return super().create(validated_data)


