# coding=utf-8
from django.views.generic import View
from django.contrib.auth.decorators import login_required


# 找到对应的视图函数，然后在视图函数上添加装饰器
class LoginRequiredView(View):
    @classmethod
    def as_view(cls, **initkwargs):
        func = super().as_view(**initkwargs)
        return login_required(func)


# 上面代码的缺点：将登录验证与类视图进行了绑定
# 多继承，扩展类
class LoginRequiredViewMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        #通用视图的as_view()是通过请求方式获得视图函数
        func = super().as_view(**initkwargs)
        return login_required(func)
