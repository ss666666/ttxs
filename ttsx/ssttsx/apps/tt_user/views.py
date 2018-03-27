from django.shortcuts import render,redirect
from django.views.generic import View
from .models import User
from django.http import HttpResponse,JsonResponse
import re
from django.core.mail import send_mail
from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer,SignatureExpired
from celery_tasks.tasks import send_user_active
from django.contrib.auth import authenticate,login



# Create your views here.

# def register(request):

    # if request.method =='GET':
    #     return render(request,'register.html')
    # elif request.method =='POST':
    #     pass

class RegisterView(View):
    def get(self,request):
        return render(request, 'register.html')
    def post(self,request):

        # 获取数据
        dict = request.POST
        uname = dict.get('user_name')
        pwd = dict.get('pwd')
        cpwd = dict.get('cpwd')
        email = dict.get('email')
        uallow = dict.get('allow')

        # 已经获得的数据
        context = {
            'uname' : uname,
            'pwd' : pwd,
            'cpwd' : cpwd,
            'email' : email,
            'err_msg' : '',
        }


        # 验证数据有效性
        # 1 判断是否接受协议
        if uallow is None:
            context['err_msg'] = '你走吧！协议都不接受～'
            return render(request, 'register.html',context)
        # 2 验证数据是否为空
        if not all([uname,pwd,cpwd,email]):
            context['err_msg'] = '你走吧！信息都不会填～'
            return render(request, 'register.html',context)
        # 3 判断密码是否一致
        if pwd != cpwd:
            context['err_msg'] = '你走吧！密码都输错了～'
            return render(request, 'register.html',context)
        # 4 用户名是否重复
        if User.objects.filter(username=uname).count() > 0:
            context['err_msg'] = '你走吧！已经有和你一样的人了～'
            return render(request, 'register.html',context)
        # 5 邮箱格式是否正确
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            context['err_msg'] = '你走吧！邮箱错了～～～'
            return render(request, 'register.html', context)

        # # 6 邮箱是否存在
        # if User.objects.filter(email=email).count()>0:
        #     context['err_msg'] = '你慢一步！邮箱已经被抢了'
        #     return render(request, 'register.html', context)

        # 保存对象
        user = User.objects.create_user(uname,email,pwd)
        user.is_active = False
        user.save()

        # # 加密用户ID
        # serializer = Serializer(settings.SECRET_KEY,60*30)
        # value = serializer.dumps({'id':user.id}).decode()
        #
        #
        # msg = '<a href="http://127.0.0.1:8000/user/active/%s">点击激活</a>'%value
        # send_mail('天天生鲜-账号激活','',settings.EMAIL_FROM,[email],html_message=msg)

        # 通知celery执行此任务，并传递参数user
        send_user_active.delay(user.id,email)

        # 提示
        return HttpResponse('历经千辛万苦，终获真经！看看邮箱我给你的宝贝～')


# 邮箱激活账户
def active(request, value):
    # 解密
    try:
        serializer = Serializer(settings.SECRET_KEY)
        dict = serializer.loads(value)
    except SignatureExpired as e:
        return HttpResponse('链接过期！！！')

    # 激活账户
    uid = dict.get('id')
    user = User.objects.get(pk=uid)
    user.is_active = True
    user.save()

    return redirect('/user/login')


# 鼠标离开后判断用户名是否重复
def exists(request):
    # 接收用户名
    uname = request.GET.get('uname')

    if uname is not None:
        # 判断用户是否存在
        result = User.objects.filter(username=uname).count()

    # 返回结果
    return JsonResponse({'result': result})



class LoginView(View):
    def get(self,request):
        uname=request.COOKIES.get('uname','')
        context={
            'title': '登录',
            'uname':uname
        }
        return render(request, 'login.html',context)

    def post(self,request):
        # 接收数据
        dict = request.POST
        uname = dict.get('username')
        upwd = dict.get('pwd')
        remember = dict.get('remember')

        # 构造返回结果
        context = {
            'uname': uname,
            'upwd': upwd,
            'err_msg': '',
            'title':'登录处理',
        }

        # 判读那数据是否填写
        if not all([uname,upwd]):
            context['err_msg'] = '请填写完信息'
            return render(request,'login.html',context)

        # 判断用户名密码是否正确
        user = authenticate(username = uname, password = upwd)

        if user is None:
            context['err_msg'] = '用户名密码错误'
            return render(request, 'login.html', context)

        # 如果未激活不能登陆
        if not user.is_active:
            context['err_msg'] = '请先到邮箱中激活'
            return render(request, 'login.html', context)

        # 状态保持
        login(request,user)

