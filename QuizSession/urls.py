from django.urls import path
from .views import basicQuizInfo,quizQuestionInsert,AcceptRecharge,AdminDashboard,EarningDetails,TotalQuiz,TotalUser,RefundUser
urlpatterns = [
    
    path('', basicQuizInfo,name='Info'),
    path('accept-recharge/', AcceptRecharge,name='accept-recharge'),
    path('admin-dashboard/', AdminDashboard,name='admin-dashboard'),
    path('admin-dashboard/earning-details/', EarningDetails,name='earning-details'),
    path('admin-dashboard/total-quiz/', TotalQuiz,name='total-quiz'),
    path('admin-dashboard/total-user/', TotalUser,name='total-user'),
    path('admin-dashboard/refund-user/', RefundUser,name='refund-user'),
    path('question-insert/<str:quizname>/', quizQuestionInsert,name='question-insert'),
    
]