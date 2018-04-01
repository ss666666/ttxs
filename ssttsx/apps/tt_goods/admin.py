from django.contrib import admin
from .models import GoodsCategory,Goods,GoodsSKU,GoodsImage,IndexGoodsBanner,IndexCategoryGoodsBanner,IndexPromotionBanner
from django.conf import settings
# from celery_tasks.tasks import generate_html
from django.shortcuts import render
import os

class BaseAdmin(admin.ModelAdmin):

    # 当数据发生添加、修改、删除时，就生成静态文件
    # 当添加对象、修改对象时，这个方法会被调用
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # generate_html.delay()
        generate_html()
    #当删除对象时，这个方法被调用
    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        # generate_html.delay()
        generate_html()


class GoodsCategoryAdmin(BaseAdmin):
    list_display = ['name', 'id', 'logo']

class IndexCategoryGoodsBannerAdmin(BaseAdmin):
    pass
class IndexPromotionBannerAdmin(BaseAdmin):
    pass
class IndexGoodsBannerAdmin(BaseAdmin):
    pass
def generate_html():
    # 查询分类信息
    category_list = GoodsCategory.objects.all()

    # 查询轮播图片
    banner_list = IndexGoodsBanner.objects.all().order_by('index')

    # 查询广告
    adv_list = IndexPromotionBanner.objects.all().order_by('index')

    # 查询每个分类的推荐产品
    for category in category_list:
        # 查询当前分类推荐的标题商品，按照index排序，去前三个
        category.title_list = IndexCategoryGoodsBanner.objects.filter(display_type=0, category=category).order_by(
            'index')[0:3]

        # 查询推荐的图片商品
        category.img_list = IndexCategoryGoodsBanner.objects.filter(display_type=1, category=category).order_by(
            'index')[0:3]

    context = {
        'title': '首页',
        'category_list': category_list,
        'banner_list': banner_list,
        'adv_list': adv_list,
    }

    response = render(None, 'index.html', context)
    # 优化 每次访问数据都一样，为了减少读数据库和渲染模板的消耗，直接将数据保存到文件中
    html = response.content.decode()
    # 将html字符串保存到文件中
    with open(os.path.join(settings.GENERATE_HTML, 'index.html'), 'w') as f1:
        f1.write(html)

    return response

admin.site.register(GoodsCategory,GoodsCategoryAdmin)
admin.site.register(Goods)
admin.site.register(GoodsSKU)
admin.site.register(GoodsImage)
admin.site.register(IndexCategoryGoodsBanner,IndexCategoryGoodsBannerAdmin)
admin.site.register(IndexPromotionBanner,IndexPromotionBannerAdmin)
admin.site.register(IndexGoodsBanner,IndexGoodsBannerAdmin)