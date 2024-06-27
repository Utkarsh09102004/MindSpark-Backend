import asyncio
import json
from datetime import datetime, timedelta
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from .models import Session, SessionUser, Question
import pytz



User = get_user_model()

class QuizSessionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("WebSocket connection requested.")
        self.unique_code = self.scope['url_route']['kwargs']['unique_code']
        self.user = self.scope['user']
        print(f"Unique code: {self.unique_code}, User: {self.user}")

        self.session = await sync_to_async(Session.objects.get)(unique_code=self.unique_code)
        print(f"Session retrieved: {self.session}")

        if self.session and self.user.is_authenticated:
            print("User is authenticated and session is valid.")
            await self.add_user_to_session()
            await self.channel_layer.group_add(self.unique_code, self.channel_name)
            await self.accept()
            # Schedule the task to send questions at the session start time
            await self.schedule_send_questions()
        else:
            print("Authentication failed or session is invalid. Closing connection.")
            await self.close()

    @sync_to_async
    def add_user_to_session(self):
        print("Adding user to session.")
        if not SessionUser.objects.filter(session=self.session, user=self.user).exists():
            SessionUser.objects.create(session=self.session, user=self.user, name=self.user.username, points=0,
                                       is_connected=True)
            print(f"User {self.user.username} added to session {self.session.unique_code}.")
        else:
            session_user = SessionUser.objects.get(session=self.session, user=self.user)
            session_user.is_connected = True
            session_user.save()
            print(f"User {self.user.username} already in session. Updated connection status.")

    async def disconnect(self, close_code):
        print(f"WebSocket connection closing with code: {close_code}")
        await self.remove_user_from_session()
        await self.channel_layer.group_discard(self.unique_code, self.channel_name)
        # Cancel the send questions task if it's running
        if hasattr(self, 'send_questions_task'):
            self.send_questions_task.cancel()
            print("Cancelled send_questions_task.")

    @sync_to_async
    def remove_user_from_session(self):
        print("Removing user from session.")
        try:
            session_user = SessionUser.objects.get(session=self.session, user=self.user)
            session_user.is_connected = False
            session_user.save()
            print(f"User {self.user.username} disconnected from session {self.session.unique_code}.")
        except SessionUser.DoesNotExist:
            print("User not found in session.")

    async def schedule_send_questions(self):
        print("Scheduling send_questions task.")
        kolkata_tz = pytz.timezone('Asia/Kolkata')
        current_time = datetime.now(kolkata_tz)
        start_time = self.session.start_time

        # Ensure start_time is correctly set and converted to the Asia/Kolkata timezone
        if start_time.tzinfo is None:
            # If start_time is naive, assume it is in UTC and convert to Asia/Kolkata timezone
            start_time = pytz.utc.localize(start_time).astimezone(kolkata_tz)
        else:
            # If start_time is aware, convert to Asia/Kolkata timezone if it's not already
            start_time = start_time.astimezone(kolkata_tz)

        print(f"Current time: {current_time}, Start time: {start_time}")

        delay = (start_time - current_time).total_seconds()
        print(f"Delay until start time: {delay} seconds")

        if delay > 0:
            await asyncio.sleep(delay)

        self.send_questions_task = asyncio.create_task(self.send_questions())
        print("Started send_questions_task.")

    async def send_questions(self):
        print("Starting to send questions.")
        questions = await sync_to_async(list)(self.session.questions.all())
        print(f"Fetched {len(questions)} questions.")

        for question in questions:
            question_data = {
                'id': question.id,
                'question_text': question.question_text,
                'options': question.options,
                'time_needed': str(question.time_needed),
            }
            print(f"Sending question ID: {question.id}")

            # Send the question to the group
            await self.channel_layer.group_send(
                self.unique_code,
                {
                    'type': 'send_question_to_clients',
                    'question': question_data
                }
            )
            print(f"Question ID {question.id} sent to group.")

            # Save the question start time
            self.question_start_time = datetime.now()
            print(f"Question start time: {self.question_start_time}")

            # Wait for time_needed + 4 seconds before sending the next question
            wait_time = question.time_needed.total_seconds() + 4
            print(f"Waiting for {wait_time} seconds before sending the next question.")
            await asyncio.sleep(wait_time)
            print(f"Waited for {wait_time} seconds, ready to send the next question.")

    async def send_question_to_clients(self, event):
        print(f"Sending question to clients: {event['question']}")
        await self.send(text_data=json.dumps(event['question']))
        print("Question sent to clients.")

    async def receive(self, text_data):
        print(f"Received message: {text_data}")
        data = json.loads(text_data)
        answer = data.get('answer')
        question_id = data.get('question_id')
        print(f"Parsed data - Answer: {answer}, Question ID: {question_id}")

        if answer is not None and question_id is not None:
            print("Processing answer.")
            await self.process_answer(answer, question_id)

    @sync_to_async
    def process_answer(self, answer, question_id):
        print("Starting process_answer function.")
        session_user = SessionUser.objects.get(session=self.session, user=self.user)
        print(f"SessionUser retrieved: {session_user}")

        question = Question.objects.get(id=question_id)  # Fetch the question using the ID
        print(f"Question retrieved: {question}")

        if answer == question.correct_answer:
            print("Answer is correct.")

            # Calculate the time taken to answer
            time_taken = (datetime.now() - self.question_start_time).total_seconds()
            print(f"Time taken to answer: {time_taken} seconds")

            max_time = question.time_needed.total_seconds()
            print(f"Max time allowed for question: {max_time} seconds")

            # Example point calculation based on speed of answer
            points = max(0, int((max_time - time_taken) / max_time * 100))  # Adjust the formula as needed
            print(f"Points calculated: {points}")

            session_user.points += points
            session_user.save()
            print(f"Updated session user points: {session_user.points}")
        else:
            print("Answer is incorrect.")

        print("Ending process_answer function.")
