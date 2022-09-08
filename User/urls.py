from django.urls import path
from .views import Login,Register,Userview,RechargeUser,QuizList,QuizTest,QuizEnd,QuizDetails,ShowResult,logout,MyQuizList,RequestForRefund
urlpatterns = [
    
    path('', Login,name='login'),
    path('test/<str:quiz>/<int:val>/', QuizTest,name='test'),
    path('signup/', Register,name='signup'),
    path('logout/', logout,name='logout'),
    path('quiz-details/<str:quiz>/', QuizDetails,name='quiz-details'),
    path('show-result/<str:quiz>/', ShowResult,name='show-result'),
    path('dashboard/', Userview,name='dashboard'),
    path('dashboard/myquiz', MyQuizList,name='myquiz'),
    path('dashboard/refund-request', RequestForRefund,name='refund-request'),
    path('recharge/', RechargeUser,name='recharge'),
    path('quiz-list/',QuizList,name='quiz-list'),
    path('quiz-end/<str:quiz>/',QuizEnd,name='quiz-end')
]