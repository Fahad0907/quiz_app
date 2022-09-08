from urllib import response
from django.shortcuts import render,redirect
from django.contrib.auth.models import User, auth
from .models import UserInfo, Recharge, UserAndQuiz , UsersAnswer,Refund
from QuizSession.models import QuizInfo,QuizQuestion,SingleOption, QuizTime
from django.db import transaction
from django.http import HttpResponse
from datetime import datetime, timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Create your views here.
def Login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            if request.user.is_superuser:
                return redirect('admin-dashboard')
            else:
                return redirect('dashboard')
        else:
            messages.info(request,'Wrong user Id or password')
    return render(request,'login.html')

def logout(request):
    auth.logout(request)
    return redirect("/")

def Register(request):
    if request.method == "POST":
        username = request.POST['username'] 
        full_name = request.POST['full_name'] 
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']  
        print(username,email,password1,password2)
        if password1 == password2:
            if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
                messages.info(request,'User already exists')
            else:
                user = User.objects.create_user(username=username,first_name=full_name ,email=email, password=password2)
                user.save()
                return redirect('login')
        else:
            messages.info(request,'password not match')  
    return render(request,'register.html')

@login_required(login_url='/')
def Userview(request):
    if request.method == "GET":
        user = UserInfo.objects.get(user=request.user)
        return render(request, 'userview.html',{'name' : user.user, 'amount': user.amount})

@login_required(login_url='/')
def RechargeUser(request):
    if request.method == "POST":
        transaction_id = request.POST['transaction']
        phone = request.POST['phone']
        amount = request.POST['amount']
        print(transaction_id,phone,amount)
        recharge = Recharge.objects.create(user=request.user,transaction_id=transaction_id,phone=phone,amount=amount)
        recharge.save()
        return redirect('dashboard')
    user = UserInfo.objects.get(user=request.user)
    return render(request,'recharge.html',{'name' : user.user, 'amount': user.amount})

@login_required(login_url='/')
def QuizList(request):
    if request.method == "GET":
        query = QuizInfo.objects.all().order_by('quiz_type')
        mainList = []
        for i in query:
            json = {}
            check_taken_quiz = UserAndQuiz.objects.filter(user=request.user,quiz_id=i.id)
            if len(check_taken_quiz) == 0:
                json['quiz_name'] = i.quiz_name
                json['quiz_type'] = i.quiz_type
                json['price'] = i.price
                mainList.append(json) 
        user = UserInfo.objects.get(user=request.user)
        return render(request,'quizList.html',{'name' : user.user, 'amount': user.amount,'context':mainList})

@login_required(login_url='/')
def QuizTest(request,quiz,val):
    quizz = QuizInfo.objects.get(quiz_name=quiz)
    quiz_time = QuizTime.objects.get(quiz=quizz)
    user = UserInfo.objects.get(user=request.user)
    quiz_start, created = UserAndQuiz.objects.get_or_create(user=request.user,quiz=quizz)
    if created:
        quiz_start.created_at=datetime.now(timezone.utc)
        quiz_start.save()
    query = QuizQuestion.objects.filter(quiz=quizz)
    
    time = quiz_time.time * 60
    now = datetime.now(timezone.utc)
    then = quiz_start.created_at
    duration = now -   then                      
    duration_in_s = duration.total_seconds() 
    print(duration_in_s)
    if request.method == "POST":
        received_option_from_user = request.POST.getlist('option')
        received_question = request.POST['queId']
        if quiz_time.time_option == 'overall' and duration_in_s > time:
            messages.info(request,'Your time is finished')
            return redirect('quiz-end',quiz=quiz)
        if quiz_time.time_option == 'perquestion' and duration_in_s > time:
            answer = UsersAnswer.objects.create(identity=quiz_start,question = received_question)
            answer.save()
            messages.info(request,'Your previous answer was not accepted due to time delay')
            quiz_start.created_at=datetime.now(timezone.utc)
            quiz_start.save()
        else:
            if quiz_time.time_option == 'perquestion':
                quiz_start.created_at=datetime.now(timezone.utc)
                quiz_start.save()
            if len(received_option_from_user) == 0:
                answer = UsersAnswer.objects.create(identity=quiz_start,question = received_question)
                answer.save()
            else:
                for i in received_option_from_user:
                    answer = UsersAnswer.objects.create(identity=quiz_start,question = received_question,answer=i)
                    answer.save()
        val +=1
        if val>len(query):
            return redirect('quiz-end',quiz=quiz)
        return redirect('test',quiz=quiz,val=val)
    
    if quiz_start.is_submit:
        return render(request,'error.html',{'name' : user.user, 'amount': user.amount,'message':"You have already taken this quiz"}) 
    query = query[val-1:val]
    mainList = []
    count = 1
    for i in query:
        basic={}
        basic['id'] = i.id
        basic['question'] = i.question
        opt = []
        option = SingleOption.objects.filter(question=i.id)
        for j in option:
            optionList = {}
            optionList['name']=j.name
            optionList['id']=j.id
            opt.append( optionList)
        basic['option'] = opt
        mainList.append(basic)
            #print(mainList)
    return render(request,'test.html',{'context':mainList,'name' : user.user, 'amount': user.amount})

@login_required(login_url='/')
def QuizEnd(request,quiz):
    try:
        quizz = QuizInfo.objects.get(quiz_name=quiz)
        user_and_quiz = UserAndQuiz.objects.get(user=request.user,quiz=quizz)
        user_answer = UsersAnswer.objects.filter(identity=user_and_quiz)
        if request.method == "GET":         
            user = UserInfo.objects.get(user=request.user)
            return render(request,'quizEnd.html',{'name' : user.user, 'amount': user.amount})
        elif 'retakeButton' in request.POST:
            if user_and_quiz.retake == quizz.retake:
                user_and_quiz.is_submit = True
                user_and_quiz.save()
                return redirect('show-result', quiz=quiz)
            user_answer.delete()
            user_and_quiz.created_at = datetime.now(timezone.utc)
            user_and_quiz.retake +=1
            user_and_quiz.save()
            return redirect('test',quiz=quiz,val=1)
        elif 'submit' in request.POST:
            user_and_quiz.is_submit = True
            user_and_quiz.save()
            return redirect('show-result', quiz=quiz)
    except:
        user = UserInfo.objects.get(user=request.user)
        return render(request,'error.html',{'name' : user.user, 'amount': user.amount,'message':" Error"})
    
@login_required(login_url='/')
def QuizDetails(request,quiz):
    try:
        user = UserInfo.objects.get(user=request.user)
        current_quiz = QuizInfo.objects.get(quiz_name=quiz)
        time = QuizTime.objects.get(quiz__quiz_name=quiz)
        if request.method == "POST":
            if current_quiz.price>0:
                if current_quiz.price> user.amount:
                    return render(request,'error.html',{'name' : user.user, 'amount': user.amount,'message':"You have not enough money, please recharge"})
                else:
                    user.amount -= current_quiz.price
                    user.save()
                    return redirect('test',quiz=quiz,val=1)
            else:
                return redirect('test',quiz=quiz,val=1)
        return render(request,'quizDetails.html',{'name' : user.user, 'amount': user.amount,'context':current_quiz,'time':time})
    except:
        user = UserInfo.objects.get(user=request.user)
        return render(request,'error.html',{'name' : user.user, 'amount': user.amount,'message':" Error"})

@login_required(login_url='/')
def ShowResult(request,quiz):
    try:
        quizz = QuizInfo.objects.get(quiz_name=quiz)
        user_and_quiz = UserAndQuiz.objects.get(user=request.user,quiz=quizz)
        if not user_and_quiz.is_submit:
            user_and_quiz.is_submit = True
            user_and_quiz.save()
        user_answer = UsersAnswer.objects.filter(identity=user_and_quiz)
        question = QuizQuestion.objects.filter(quiz__quiz_name=quiz)
        user = UserInfo.objects.get(user=request.user)
        total = 0
        mainList = []
        for i in question:
            json = {}
            correct_anwer = []
            user_answer_list = []
            all_answer = []
            answer_with_name = []
            json['question'] = i.question
                
            answer_form_db = SingleOption.objects.filter(question__question = i.question)
            user_answer = UsersAnswer.objects.filter(question=i.id,identity=user_and_quiz)
                
            for j in answer_form_db:
                name_and_solution = {}
                name_and_solution['name'] = j.name
                name_and_solution['is_answer'] = j.is_answer
                all_answer.append(name_and_solution)
                if j.is_answer:
                    correct_anwer.append(j.id)
            correct_anwer.sort()
                
            for j in user_answer:
                if j.answer:
                    answer_name = SingleOption.objects.get(id=j.answer)
                    answer_with_name.append(answer_name.name)
                    user_answer_list.append(j.answer)
            user_answer_list.sort()
                
            json['all_answer'] = all_answer
            json['your_answer'] = answer_with_name
            mainList.append(json)
            if correct_anwer == user_answer_list:
                total +=1
        user_and_quiz.result = total
        user_and_quiz.save()    
        print(total,mainList)
        return render(request, 'showResult.html',{'context':mainList,'name' : user.user, 'amount': user.amount,'total_number':len(question),'correct':total})  
    except:
        user = UserInfo.objects.get(user=request.user)
        return render(request,'error.html',{'name' : user.user, 'amount': user.amount,'message':" Error"})
        
@login_required(login_url='/')
def MyQuizList(request):
    try:
        if request.method == "GET":
            query = QuizInfo.objects.all().order_by('quiz_type')
            mainList = []
            for i in query:
                json = {}
                try:
                    check_taken_quiz = UserAndQuiz.objects.get(user=request.user,quiz_id=i.id)
                    json['quiz_name'] = check_taken_quiz.quiz.quiz_name
                    json['quiz_type'] = check_taken_quiz.quiz.quiz_type
                    json['price'] = i.price
                    json['result'] = check_taken_quiz.result
                    mainList.append(json)
                except:
                    pass                    
            user = UserInfo.objects.get(user=request.user)
            return render(request,'myQuiz.html',{'name' : user.user, 'amount': user.amount,'context':mainList})
    except:
        user = UserInfo.objects.get(user=request.user)
        return render(request,'error.html',{'name' : user.user, 'amount': user.amount,'message':" Error"})

@login_required(login_url='/')
def RequestForRefund(request):
    if request.method == "GET":
        query = QuizInfo.objects.filter(quiz_type='paid')
        mainList = []
        for i in query:
            json = {}
            try:
                check_refund = Refund.objects.filter(user=request.user,quiz_id=i.id)
                if len(check_refund):
                    continue
                check_taken_quiz = UserAndQuiz.objects.get(user=request.user,quiz_id=i.id)
                json['quiz_name'] = check_taken_quiz.quiz.quiz_name
                json['quiz_type'] = check_taken_quiz.quiz.quiz_type
                json['price'] = i.price
                json['result'] = check_taken_quiz.result
                mainList.append(json)
            except:
                pass                    
        user = UserInfo.objects.get(user=request.user)
        return render(request,'requestForRefund.html',{'name' : user.user, 'amount': user.amount,'context':mainList})
    elif request.method == "POST":
        print(request.POST['quiz'])
        quiz = QuizInfo.objects.get(quiz_name=request.POST['quiz'])
        refund, created = Refund.objects.get_or_create(user=request.user,quiz=quiz)
        if created:
            return redirect('dashboard')