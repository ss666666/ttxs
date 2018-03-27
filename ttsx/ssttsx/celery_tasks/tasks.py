from itsdangerous import TimedJSONWebSignatureSerializer as Serializer,SignatureExpired
from django.conf import settings
from django.core.mail import send_mail
from celery import Celery


import os
os.environ["DJANGO_SETTINGS_MODULE"] = "ssttsx.settings"
# 放到Celery服务器上时添加的代码
import django
django.setup()

app = Celery('celery_tasks.tasks',broker='redis://127.0.0.1:6379/6')


@app.task
def send_user_active(user_id,email):
    # 加密用户编号
    serializer = Serializer(settings.SECRET_KEY, 60 * 60 * 24 * 7)
    value = serializer.dumps({'id': user_id}).decode()

    sender = settings.EMAIL_FROM  # 发件人
    receiver = [email]  # 接收人

    # 让用户激活：向注册的邮箱发邮件，点击邮件中的链接，转到本网站的激活地址
    msg = '<a href="http://127.0.0.1:8000/user/active/%s">点击激活</a>' % value
    send_mail('天天生鲜-账户激活', '', sender, receiver , html_message=msg)

