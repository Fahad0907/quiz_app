from django.shortcuts import render,redirect
from .models import QuizInfo,QuizQuestion,SingleOption,QuizTime
from User.models import Recharge,UserInfo, UserAndQuiz,Refund, UsersAnswer
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Sum
from django.db.models import Count
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
# Create your views here.
@user_passes_test(lambda u: u.is_superuser)
def basicQuizInfo(request):
    if request.user.is_superuser:
        if request.method == "POST":
            price = 0
            quizname = request.POST['quizname']
            status = request.POST['status']
            time_status = request.POST['time_status']
            time = request.POST['time']
            retake = request.POST['retake']
            number_of_question = request.POST['questionNumber']
            question_option = request.POST['questionOption']
            image = request.POST['image']
            img = 'pics/' + image
            print(image)
            description = request.POST['about']
            print(number_of_question, question_option)
            if request.POST['price']:
                price = request.POST['price']
            quiz = QuizInfo.objects.create(quiz_name=quizname,number_of_question=number_of_question,number_of_option=question_option,
                                           quiz_type=status, retake=retake,price=price,image=img,description=description)
            quiz.save()
            quiz_time = QuizTime.objects.create(quiz=quiz,time=time,time_option=time_status)
            quiz_time.save()
            return redirect('question-insert',quizname=quizname)
        return render(request,'quizBasicInfo.html')

@user_passes_test(lambda u: u.is_superuser)
def quizQuestionInsert(request,quizname):
    quiz = QuizInfo.objects.get(quiz_name=quizname)
    if request.method == "GET":  
        return render(request,'quizQuestionInput.html',{'question': range(quiz.number_of_question),'option': range(quiz.number_of_option)})
    elif request.method == "POST": 
        question = request.POST.getlist('question')
        option = request.POST.getlist('option')
        ans = request.POST.getlist('radio')
        print(question,option,ans)
        number_of_option = quiz.number_of_option
        itr = 0
        for i in range(len(question)):
            que = QuizQuestion.objects.create(question=question[i],quiz= quiz)
            que.save()
            cnt = 1
            for j in range(itr, len(option)):
                singleOption = SingleOption.objects.create(quiz=quiz,question=que,name=option[j],is_answer=True if ans[j]=='y' else False)
                singleOption.save()
                if cnt == number_of_option:
                    break
                cnt += 1
            itr += number_of_option
        return redirect('admin-dashboard')
 
@user_passes_test(lambda u: u.is_superuser)    
def AcceptRecharge(request):
    if request.user.is_superuser:
        if request.method=="POST":
            with transaction.atomic():
                customer = User.objects.get(username=request.POST['username'])
                recharge = Recharge.objects.get(user=customer,transaction_id=request.POST['transaction'])
                recharge.confirm = True
                recharge.save()
                user = UserInfo.objects.get(user__username=customer)
                user.amount += float(request.POST['amount'])
                user.save()
            return redirect('admin-dashboard')
        query = Recharge.objects.filter(confirm=False)
        return render(request, 'acceptRecharge.html',{'context':query})

@user_passes_test(lambda u: u.is_superuser)   
def AdminDashboard(request):
    if request.method == "GET":
        earning = UserAndQuiz.objects.filter(quiz__quiz_type = 'paid').aggregate(Sum('quiz__price'))
        total_user = User.objects.filter(is_superuser = False).count()
        total_quiz = QuizInfo.objects.all().count()
        refund = Refund.objects.filter(status__isnull=True).count()
        return render(request, 'adminDashboard.html',{'earning':earning['quiz__price__sum'],'user' : total_user,'quiz':total_quiz,'refund':refund})

@user_passes_test(lambda u: u.is_superuser)
def EarningDetails(request):
    if request.method == "GET":
        query = UserAndQuiz.objects.filter(quiz__quiz_type = 'paid')
        return render(request, 'earningDetails.html',{'context':query})

@user_passes_test(lambda u: u.is_superuser)
def TotalQuiz(request):
    if request.method == "GET":
        quiz = QuizInfo.objects.all().order_by('-quiz_type')
        mainList = []
        for i in quiz:
            json = {}
            json['quiz_name'] = i.quiz_name
            json['quiz_type'] = i.quiz_type
            json['quiz_price'] = i.price
            countQuiz = UserAndQuiz.objects.filter(quiz_id=i.id).count()
            json['quiz_taken'] = countQuiz
            mainList.append(json)
        return render(request,'totalQuiz.html',{'context':mainList})
    
@user_passes_test(lambda u: u.is_superuser)
def TotalUser(request):
    if request.method == "GET":
        user = UserInfo.objects.filter(user__is_superuser=False).order_by('amount')
        mainList = []
        for i in user:
            json = {}
            json['name'] = i.user.first_name
            json['email'] = i.user.email
            json['cash'] = i.amount
            total_quiz_taken = UserAndQuiz.objects.filter(user_id=i.id).count()
            json['quiz_taken'] = total_quiz_taken
            mainList.append(json)
        return render(request,'totalUser.html',{'context':mainList})
    
@user_passes_test(lambda u: u.is_superuser)      
def RefundUser(request):
    if request.method == "POST":
        try:
            quiz = QuizInfo.objects.get(quiz_name = request.POST['quiz'])
            userinfo = UserInfo.objects.get(user_id=request.POST['userid'])
            if 'refund' in request.POST:
                userinfo.amount += quiz.price
                userinfo.save()
                user_and_quiz = UserAndQuiz.objects.get(quiz_id = quiz.id,user_id=userinfo.id)
                user_and_answer = UsersAnswer.objects.filter(identity=user_and_quiz)
                user_and_answer.delete()
                user_and_quiz.delete()
                refund = Refund.objects.get(quiz=quiz,user_id=userinfo.id)
                refund.delete()
            elif 'deny' in request.POST:
                refund = Refund.objects.get(quiz=quiz,user_id=userinfo.id)
                refund.status = 'deny'
                refund.save()
            return redirect('admin-dashboard')
        except:
            messages.info(request,'Your time is finished')
            return redirect('admin-dashboard')
    query = Refund.objects.filter(status__isnull=True)
    return render(request, 'Refund.html',{'context':query})