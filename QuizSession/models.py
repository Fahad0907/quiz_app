from django.db import models

# Create your models here.
quiz_status = (
    ('paid','paid'),
    ('free','free')
)
time_limit = (
    ('perquestion','perquestion'),
    ('overall','overall')
)

class QuizInfo(models.Model):
    quiz_name = models.CharField(unique=True,max_length=255)
    number_of_question = models.IntegerField()
    number_of_option = models.IntegerField()
    quiz_type = models.CharField(max_length=255,choices=quiz_status)
    price = models.FloatField(default=0.0,null=True,blank=True)
    image = models.ImageField(upload_to='pics')
    description = models.TextField()
    retake = models.IntegerField()
    def __str__(self) -> str:
        return self.quiz_name
    
class QuizQuestion(models.Model):
    quiz = models.ForeignKey(QuizInfo,on_delete=models.CASCADE)
    question = models.CharField(max_length=255)
    
    def __str__(self) -> str:
        return f"{self.quiz.quiz_name} - {self.question}"
    
class SingleOption(models.Model):
    quiz = models.ForeignKey(QuizInfo,on_delete=models.CASCADE)
    question = models.ForeignKey(QuizQuestion,on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    is_answer = models.BooleanField(default=False)

class QuizTime(models.Model):
    quiz = models.ForeignKey(QuizInfo,on_delete=models.CASCADE)
    time = models.IntegerField()
    time_option = models.CharField(max_length=255, choices=time_limit)
    
    def __str__(self) -> str:
        return f"{self.quiz.quiz_name} - {self.time}"