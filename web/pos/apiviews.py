import decimal
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import (HttpResponse,
                         JsonResponse,
                         HttpResponseForbidden,
                         HttpResponseBadRequest)
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from .serializers import OrderSerializer, OrderItemSerializer
from . import helper
from .models import Product, Order, Cash, Order_Item


@csrf_exempt
def current_order(request):
    _, order, _ = helper.setup_handling(request)

    if request.method == 'GET':
        serializer = OrderSerializer(order)
        return JsonResponse(serializer.data)
    elif request.method == 'DELETE':
        for item in Order_Item.objects.filter(order=order):
            if item.product.stock_applies:
                item.product.stock += 1
                item.product.save()
            item.delete()

        order.total_price = 0
        order.save()

        return HttpResponse(status=204)
    else:
        return HttpResponseBadRequest()


def current_order_items(request):
    _, order, _ = helper.setup_handling(request)

    order_items = Order_Item.objects.filter(order=order)
    serializer = OrderItemSerializer(order_items, many=True)
    return JsonResponse(serializer.data, safe=False)
