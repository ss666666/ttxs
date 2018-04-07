from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from tt_goods.models import GoodsSKU
from django_redis import get_redis_connection
from django.http import Http404, JsonResponse
from .models import OrderInfo, OrderGoods
import uuid
from django.db import transaction
from django.db.models import F



@login_required
def index(request):

    # 接收商品编号
    sku_ids = request.GET.getlist('sku_id')

    # 查询用户的收货地址
    addr_list = request.user.address_set.all()

    # 查询商品信息
    sku_list = []
    redis_client = get_redis_connection()
    key = 'cart%d' % request.user.id
    for sku_id in sku_ids:
        sku = GoodsSKU.objects.get(pk = sku_id)
        sku.cart_count = int(redis_client.hget(key,sku_id))
        sku_list.append(sku)


    context = {
        'title' : '订单处理',
        'addr_list': addr_list,
        'sku_list' : sku_list,
    }

    return render(request, 'place_order.html', context)


@login_required
def handle(request):
    if request.method != 'POST':
        return Http404

    # 接收数据
    dict = request.POST
    addr_id = dict.get('addr_id')
    pay_style = dict.get('pay_style')
    sku_ids = dict.get('sku_ids')
    print(dict)
    # 验证数据是否存在
    if not all([addr_id, pay_style, sku_ids]):
        return JsonResponse({'status' : 2})

    # 开启事务
    sid = transaction.savepoint()

    # 1 创建订单对象
    order_info = OrderInfo()
    order_info.order_id = str(uuid.uuid1())
    # 用户
    order_info.user = request.user
    # 收货地址
    order_info.address_id = int(addr_id)
    # 商品数量
    order_info.total_count = 0
    # 商品总价
    order_info.total_amount = 0
    # 运费
    order_info.trans_cost = 10
    # 支付方式
    order_info.pay_method = int(pay_style)

    order_info.save()

    # 构造redis的连接与键
    redis_client = get_redis_connection()
    key = 'cart%d' % request.user.id

    # 2 遍历所有商品信息，判断库存是否足够
    is_ok = True
    sku_ids = sku_ids.split(',')
    sku_ids.pop()
    total_count = 0
    total_amount = 0
    for sku_id in sku_ids:
        sku = GoodsSKU.objects.get(pk = sku_id)
        cart_count = int(redis_client.hget(key,sku_id))

        # 加入乐观锁,返回值表示受影响的行数
        result = GoodsSKU.objects.filter(pk=sku_id, stock__gte=cart_count).update(stock=F('stock') - cart_count,sales=F('sales') + cart_count)

        # 3 库存足够继续处理
        if result:
            # 3.1 创建详细数据
            order_goods = OrderGoods()
            # 订单
            order_goods.order = order_info
            # 商品
            order_goods.sku = sku
            # 数量
            order_goods.count = cart_count
            # 价格
            order_goods.price = sku.price
            order_goods.save()

            # 计算总量
            total_count += cart_count
            total_amount += sku.price*cart_count

            # 删除购物车信息
            redis_client.hdel(key,sku_id)

        # 库存不足直接返回
        else:
            is_ok = False
            break

    if is_ok:
        # 保存总数量、总价
        order_info.total_count = total_count
        order_info.total_amount = total_amount
        order_info.save()

        # 此逻辑表示整个循环都正常运行完成，数据有效
        transaction.savepoint_commit(sid)

        # 删除购物车信息
        for sku_id in sku_ids:
            redis_client.hdel(key, sku_id)

        return JsonResponse({'status':1})
    else:
        # 当前逻辑表示某个商品库存不足，之前成功的数据库操作都放弃
        transaction.savepoint_rollback(sid)

        return JsonResponse({'status':3})