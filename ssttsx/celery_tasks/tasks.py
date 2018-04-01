from itsdangerous import TimedJSONWebSignatureSerializer as Serializer,SignatureExpired
from django.conf import settings
from django.core.mail import send_mail
from celery import Celery
# from tt_goods.models import GoodsCategory,Goods,GoodsSKU,GoodsImage,IndexGoodsBanner,IndexCategoryGoodsBanner,IndexPromotionBanner
# from django.shortcuts import render
# import os


app=Celery('celery_tasks.tasks',broker='redis://127.0.0.1:6379/6')


@app.task
def send_user_active(user_id,email):
    # 加密用户编号
    serializer = Serializer(settings.SECRET_KEY, 60 * 60 * 24 * 7)
    value = serializer.dumps({'id': user_id}).decode()

    sender = settings.EMAIL_FROM  # 发件人
    receiver = [email]  # 接收人

    # 让用户激活：向注册的邮箱发邮件，点击邮件中的链接，转到本网站的激活地址
    msg = '<a href="http://127.0.0.1:8000/user/active/%s">点击激活</a>' % value
    send_mail('天天生鲜-账户激活', '', sender, receiver, html_message=msg)




# @app.task
# def generate_html():
#     # 查询分类信息
#     category_list = GoodsCategory.objects.all()
#
#     # 查询轮播图片
#     banner_list = IndexGoodsBanner.objects.all().order_by('index')
#
#     # 查询广告
#     adv_list = IndexPromotionBanner.objects.all().order_by('index')
#
#     # 查询每个分类的推荐产品
#     for category in category_list:
#         # 查询当前分类推荐的标题商品，按照index排序，去前三个
#         category.title_list = IndexCategoryGoodsBanner.objects.filter(display_type=0, category=category).order_by(
#             'index')[0:3]
#
#         # 查询推荐的图片商品
#         category.img_list = IndexCategoryGoodsBanner.objects.filter(display_type=1, category=category).order_by(
#             'index')[0:3]
#
#     context = {
#         'title': '首页',
#         'category_list': category_list,
#         'banner_list': banner_list,
#         'adv_list': adv_list,
#     }
#
#     response = render(None, 'index.html', context)
#     # 优化 每次访问数据都一样，为了减少读数据库和渲染模板的消耗，直接将数据保存到文件中
#     html = response.content.decode()
#     # 将html字符串保存到文件中
#     with open(os.path.join(settings.GENERATE_HTML, 'index.html'), 'w') as f1:
#         f1.write(html)
#
#     return response

