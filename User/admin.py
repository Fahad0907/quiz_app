from django.contrib import admin
from .models import UserInfo,Recharge,UserAndQuiz,UsersAnswer
# Register your models here.
admin.site.register(UserInfo)
admin.site.register(Recharge)
admin.site.register(UserAndQuiz)
admin.site.register(UsersAnswer)
