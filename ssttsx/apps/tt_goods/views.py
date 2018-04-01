from django.shortcuts import render
from .models import GoodsCategory,  IndexGoodsBanner, IndexCategoryGoodsBanner, IndexPromotionBanner, GoodsSKU
# Create your views here.
import os
from django.conf import settings
from django.core.cache import cache
from django.http import Http404
from django_redis import get_redis_connection
from django.core.paginator import Paginator,Page
from utils.page_list import get_page_list
from haystack.generic_views import SearchView


def fdfs_test(request):
    category = GoodsCategory.objects.get(pk = 1)
    context = {'category': category}
    return render(request,'fdfs_text.html',context)

def index(request):

    # 从缓存中读取数据
    context = cache.get('index2')

    if context is None:
        # 查询分类信息
        category_list = GoodsCategory.objects.all()

        # 查询轮播图片
        banner_list = IndexGoodsBanner.objects.all().order_by('index')

        # 查询广告
        adv_list = IndexPromotionBanner.objects.all().order_by('index')

        # 查询每个分类的推荐产品
        for category in category_list:

            # 查询当前分类推荐的标题商品，按照index排序，去前三个
            category.title_list = IndexCategoryGoodsBanner.objects.filter(display_type=0, category = category).order_by('index')[0:3]

            # 查询推荐的图片商品
            category.img_list = IndexCategoryGoodsBanner.objects.filter(display_type=1, category = category).order_by('index')[0:3]


        context = {
            'title':'首页',
            'category_list': category_list,
            'banner_list': banner_list,
            'adv_list': adv_list,
        }

        cache.set('index2',context, 600)
        #
    response = render(request,'index.html',context)


    return response


def detail(request, sku_id):
    # 查询商品信息
    try:
        sku = GoodsSKU.objects.get(pk=sku_id)
    except:
        raise Http404()

    # 查询分类信息
    category_list = GoodsCategory.objects.all()

    # 查询新品推荐:当前商品所在分类的最新两个商品
    # 根据多找一
    category = sku.category
    # 根据一找多：分类对象.模型类小写_set
    new_list = category.goodssku_set.all().order_by('-id')[0:2]

    # 查询当前商品对应的所有陈列
    # 根据当前sku找到对应的spu，
    goods = sku.goods
    # 根据spu找所有的sku，
    other_list = goods.goodssku_set.all()

    # 最近浏览
    if request.user.is_authenticated():
        redis_client = get_redis_connection()
        # 构造键
        key = 'history%d' % request.user.id
        # 如果当前编号已存在，删除
        # 删除所有的指定元素
        redis_client.lrem(key,0,sku_id)
        # 将当前编号加入,向列表的左侧添加一个元素
        redis_client.lpush(key,sku_id)
        # 不能超过5个
        if redis_client.llen(key) > 5:
            # 从列表的右侧删除一个元素
            redis_client.rpop(key)


    context = {
        'title':'商品详情',
        'sku':sku,
        'category_list':category_list,
        'new_list':new_list,
        'other_list':other_list,

    }



    return render(request, 'detail.html', context)



def list_sku(request, category_id):
    # 查询当前分类对象
    try:
        category_now=GoodsCategory.objects.get(pk=category_id)
    except:
        raise Http404()

    # 排序规则
    order = int(request.GET.get('order', 1))
    # 按照价格降序
    if order == 2:
        order_by = '-price'
    # 按照价格升序
    elif order == 3:
        order_by = 'price'
    # 按照销量降序
    elif order == 4:
        order_by = '-sales'
    # 默认按照编号排序
    else:
        order_by = '-id'


    # 查询当前分类的所有商品
    sku_list = GoodsSKU.objects.filter(category_id=category_id).order_by(order_by)

    # 查询所有的分类信息
    category_list = GoodsCategory.objects.all()

    # 查询当前分类的最新的两个商品
    new_list = category_now.goodssku_set.all().order_by('-id')[0:2]

    # 分页
    paginator = Paginator(sku_list,5)
    # 总页数
    total_page = paginator.num_pages
    # 接收页码值然后判断
    pindex = int(request.GET.get('pindex',1))
    if pindex < 1:
        pindex = 1
    if pindex > total_page:
        pindex = total_page
    # 查询指定页码数据
    page = paginator.page(pindex)

    page_list = get_page_list(total_page,pindex)

    context={
        'title':'商品列表',
        'page':page,
        'category_list':category_list,
        'category_now':category_now,
        'new_list':new_list,
        'order': order,
        'page_list':page_list,

    }

    return render(request,'list.html',context)


class MySearchView(SearchView):
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title']='搜索结果'
        context['category_list']=GoodsCategory.objects.all()

        #页码控制
        total_page=context['paginator'].num_pages
        pindex=context['page_obj'].number
        context['page_list']=get_page_list(total_page,pindex)

        return context