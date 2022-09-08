from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from QuizSession.models import QuizInfo
# Create your models here.
refund_option = (
    ('deny','deny'),
    ('accept','accept')
)

class UserInfo(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    amount = models.FloatField(default=0)
    
    def __str__(self) -> str:
        return self.user.username

@receiver(post_save,sender=User)
def create_user_info(sender, instance, created,**kwargs):
    if created:
        UserInfo.objects.create(user=instance)
        
        
class Recharge(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=255,unique=True)
    confirm = models.BooleanField(default=False)
    phone = models.CharField(max_length=11)
    amount = models.FloatField()
    def __str__(self) -> str:
        return f"{self.user.username} - {self.transaction_id}"
    
    
class UserAndQuiz(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    quiz = models.ForeignKey(QuizInfo,on_delete=models.CASCADE)
    created_at = models.DateTimeField(null=True,blank=True)
    is_submit = models.BooleanField(default=False)
    result = models.IntegerField(default=0)
    retake = models.IntegerField(default=0)
    def __str__(self) -> str:
        return f"{self.user.username} - {self.quiz.quiz_name}"
    
class UsersAnswer(models.Model):
    identity = models.ForeignKey(UserAndQuiz,on_delete=models.CASCADE)
    question = models.IntegerField()
    answer = models.IntegerField(null=True,blank=True)
    
    
class Refund(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    quiz = models.ForeignKey(QuizInfo,on_delete=models.CASCADE)
    status = models.CharField(max_length=255,choices=refund_option,null=True,blank=True)
    def __str__(self) -> str:
        return f"{self.user.username} - {self.quiz.quiz_name}"
    
    
    

    