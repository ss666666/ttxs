from django.shortcuts import render
from django.http import JsonResponse, Http404
from tt_goods.models import GoodsSKU
import json
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

    response = JsonResponse({'status' : 1 })

    # 区分用户是否登陆
    if request.user.is_authenticated():

        # 如果登陆，将购物车信息存到redis里
        pass
    else:
        # 如果没有登陆，将信息存到cookies里
        # 存储数据的格式：{1:2,2:2}
        cart_dict = {}
        #读取cookies中信息，加入字典中
        cart_dict = json.loads(cart_dict)
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
