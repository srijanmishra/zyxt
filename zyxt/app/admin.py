from django.contrib import admin
from zyxt.app import models

class UserProfileAdmin(admin.ModelAdmin):
    fields = ('name', 'username', 'email',)

class LevelAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'user', 'level', 'modified',)
    list_filter = ('quiz', 'level',)

class QuestionAdmin(admin.ModelAdmin):
    search_fields = ('question',)
    list_display = ('question', 'quiz', 'level',)
    list_filter = ('quiz', 'level',)

admin.site.register(models.Quiz)
admin.site.register(models.Question, QuestionAdmin)
admin.site.register(models.UserProfile, UserProfileAdmin)
admin.site.register(models.Level, LevelAdmin)
