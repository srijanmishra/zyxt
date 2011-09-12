from django.db import models
from django.contrib.auth.models import User, UserManager
from datetime import datetime

class Quiz(models.Model):
    DISPLAY_CHOICES = (
               ('Y', 'Yes'),
               ('N', 'No'),
               )
    
    name = models.CharField(max_length=30)
    short_description = models.CharField(max_length=200)
    long_description = models.TextField()
    display = models.CharField(max_length=1, choices=DISPLAY_CHOICES, default='N')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Quizzes'
    
    def __unicode__(self):
        return self.name
    
    def is_closed(self):
        now = datetime.now()
        
        if self.start_time and self.start_time > now:
            return u'The quiz has not started yet. Kindly check later.'
        if self.end_time and self.end_time < now:
            return u'The quiz has ended. You can try other quizzes.'
        if self.display == 'N':
            return u'This quiz is not open yet. Kindly check later.'
        
        return False
    
    def has_questions(self):
        if self.question_set.all():
            return True
        else:
            return False

class Question(models.Model):
    level = models.IntegerField()
    question = models.TextField()
    answers = models.TextField()
    quiz = models.ForeignKey(Quiz)
    
    class Meta:
        unique_together = (('level', 'quiz'),)
        ordering = ['-quiz', '-level']
    
    def __unicode__(self):
        return self.question

class UserProfile(User):
    name = models.CharField(max_length=30)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    
    objects = UserManager()
    
    def __unicode__(self):
        return self.name

class Level(models.Model):
    user = models.ForeignKey(UserProfile)
    quiz = models.ForeignKey(Quiz)
    level = models.IntegerField(default=1)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'quiz', 'level')
        ordering = ['-quiz', '-level', '-modified']
    
    def __unicode__(self):
        return '%s - Level %d' % (self.user.username, self.level)
