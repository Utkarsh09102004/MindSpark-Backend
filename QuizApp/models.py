from django.contrib.auth.models import User
from django.db import models
import string
import random

class Session(models.Model):
    start_time = models.DateTimeField()
    max_participants = models.IntegerField()
    unique_code = models.CharField(max_length=6, unique=True)
    quiz_master = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_master_sessions')
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.unique_code:
            self.unique_code = self.generate_unique_code()
        super(Session, self).save(*args, **kwargs)

    def generate_unique_code(self):
        length = 6
        characters = string.ascii_letters + string.digits
        while True:
            code = ''.join(random.choice(characters) for _ in range(length))
            if not Session.objects.filter(unique_code=code).exists():
                return code

# Question model
class Question(models.Model):
    question_text = models.CharField(max_length=255)
    options = models.JSONField()
    correct_answer = models.CharField(max_length=255)
    time_needed = models.DurationField()
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='questions')

# SessionUser model
class SessionUser(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_sessions')
    name = models.CharField(max_length=255)
    points = models.IntegerField(default=0)
    is_connected = models.BooleanField(default=True)