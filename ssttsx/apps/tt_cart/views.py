from django.shortcuts import render
from django.http import JsonResponse, Http404
from tt_goods.models import GoodsSKU
import json
from django_redis import get_redis_connection
# Create your views here.

def add(request):


    if request.method != 'POST':
        return Http404

    # 接收商品编号，数量
    dict = request.POST
    sku_id = dict.get('sku_id')
    count = int(dict.get('count', 0))

    # 验证数据有效性
    # 判读那商品编号是否合法
    if GoodsSKU.objects.filter(id = sku_id).count() <= 0:
        return JsonResponse({'status' : 2 })
    # 判读数量是否合法
    if count <= 0:
        return JsonResponse({'status' : 3})
    if count >= 5:
        count = 5


    # 区分用户是否登陆
    if request.user.is_authenticated():
        # 如果登陆，将购物车信息存到redis里
        redis_client = get_redis_connection()
        key = 'cart%d' % request.user.id

        # 判断商品是否存在
        if redis_client.hexists(key,sku_id):
            # 存在相加
            count1 = int(redis_client.hget(key,sku_id))
            count2 = count
            count0 = count1 + count2
            if count0 > 5:
                count0 = 5
            redis_client.hset(key, sku_id, count0)
        else:
            # 商品不存在则添加
            redis_client.hset(key, sku_id, count)
        # 计算购物车总量
        total_count = 0
        for v in redis_client.hvals(key):
            total_count += int(v)

        # 返回结果
        response = JsonResponse({'status' : 1, 'total_count' : total_count})

    else:
        # 如果没有登陆，将信息存到cookies里
        cart_dict = {}
        #读取cookies中信息，加入字典中
        cart_str = request.COOKIES.get('cart')

        if cart_str:
            cart_dict = json.loads(cart_str)
        # 判断是否有商品
        if sku_id in cart_dict:
            # 有
            count1 = cart_dict[sku_id]
            count0 = count1 + count
            if count0 > 5:
                count0 = 5
            cart_dict[sku_id] = count0
        else:
            # 如果商品不存在，则添加
            cart_dict[sku_id] = count

        #计算总数
        total_count = 0
        for k, v in cart_dict.items():
            # total_count+=1
            total_count += v

        # 将字典转成字符串，用于存入cookie中
        cart_str = json.dumps(cart_dict)
        response = JsonResponse({'status': 1, 'total_count': total_count})

        # 写入cookie
        response.set_cookie('cart', cart_str, expires=60 * 60 * 24 * 14)



    return response


def index(request):
    sku_list = []

    # 查询购物车中的信息
    if request.user.is_authenticated():
        # 如果登陆的话就从redis中读取信息
        redis_client = get_redis_connection()
        key = 'cart%d' % request.user.id
        # 获取所有商品编号
        id_list = redis_client.hkeys(key)
        # 遍历
        for id1 in id_list:
            sku = GoodsSKU.objects.get(pk = id1)
            # 购物车数量
            sku.cart_count = int(redis_client.hget(key,id1))
            sku_list.append(sku)

    else:
        # 没有登录就从cookie中读取
        cart_str = request.COOKIES.get('cart')
        # 判断cookie中是否有数据
        if cart_str:
            # 将字符串转换成字典
            cart_dict = json.loads(cart_str)

            # 遍历字典
            for k, v in cart_dict.items():
                # 根据商品编号查询商品对象
                sku = GoodsSKU.objects.get(pk = k)
                sku.cart_count = v
                sku_list.append(sku)
    context = {
        'title' : '购物车',
        'sku_list' : sku_list,
    }


    return render(request,'cart.html',context)


def edit(request):
    if request.method != 'POST':
        return Http404

    # 接受参数
    dict = request.POST
    sku_id = dict.get('sku_id',0)
    count = dict.get('count',0)


    # 判断商品是否存在
    if GoodsSKU.objects.filter(pk=sku_id).count() <= 0:
        return JsonResponse({'status' : 2})
    # 验证数据有效行
    try:
        count = int(count)
    except:
        return JsonResponse({'status' : 3})
    # 判断数量
    if count <= 0:
        count = 1
    elif count >= 5:
        count = 5

    response = JsonResponse({'status' : 1})

    if request.user.is_authenticated():
        print('123')
        # 登录操作redis
        redis_client = get_redis_connection()
        redis_client.hset('cart%d' % request.user.id, sku_id, count)
    else:
        print('123')
        # 如果没有登录操作cookie
        cart_str = request.COOKIES.get('cart')
        if cart_str:
            cart_dict = json.loads(cart_str)
            # 改写数量
            cart_dict[sku_id] = count
            # 将字典转成字符串用于cookie保存
            cart_str = json.dumps(cart_dict)
            # 写入cookie，保存信息
            response.set_cookie('cart', cart_str,expires=60 * 60 * 24 * 7)

    return response


def delete(request):
    if request.method != 'POST':
        return Http404()
    sku_id = request.POST.get('sku_id')

    response = JsonResponse({'status': 1})

    if request.user.is_authenticated():
        redis_client = get_redis_connection()
        redis_client.hdel('cart%d' % request.user.id, sku_id)
    else:
        cart_str = request.COOKIES.get('cart')
        if cart_str:
            cart_dict = json.loads(cart_str)
            cart_dict.pop(sku_id)
            cart_str = json.dumps(cart_dict)
            response.set_cookie('cart', cart_str, expires=60 * 60 * 24 * 14)
    return response


