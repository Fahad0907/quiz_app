from django.contrib import admin
from .models import  QuizQuestion, QuizInfo , QuizTime,SingleOption
# Register your models here.
admin.site.register(QuizQuestion)
admin.site.register(SingleOption)
admin.site.register(QuizInfo )
admin.site.register(QuizTime)

