import logging
import decimal
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import (HttpResponse,
                         JsonResponse,
                         HttpResponseBadRequest)
from rest_framework import status
from .serializers import OrderSerializer, OrderItemSerializer
from .helper import (get_current_user_order,
                     get_can_negative_stock,
                     product_list_from_order)
from .models import Product, Order_Item, Order, Cash


@csrf_exempt
def current_order(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    order = get_current_user_order(request.user.username)

    if request.method == 'DELETE':
        for item in Order_Item.objects.filter(order=order):
            if item.product.stock_applies:
                item.product.stock += 1
                item.product.save()
            item.delete()

        order.total_price = 0
        order.save()

    serializer = OrderSerializer(order)
    return JsonResponse(serializer.data, safe=False)


def current_order_items(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    order = get_current_user_order(request.user.username)

    order_items = Order_Item.objects.filter(order=order)
    serializer = OrderItemSerializer(order_items, many=True)
    return JsonResponse(serializer.data, safe=False)


@csrf_exempt
def current_order_item(request, item_id):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    order = get_current_user_order(request.user.username)

    if request.method == 'DELETE':
        order_item = get_object_or_404(Order_Item, id=item_id)
        order_product = order_item.product

        if order_product.stock_applies:
            order_product.stock += 1
            order_product.save()

        order.total_price = (
            order.total_price -
            order_item.price).quantize(
                decimal.Decimal('0.01'))

        if order.total_price < 0:
            logging.error("prices below 0! "
                          "You might be running in to the "
                          "10 digit total order price limit")
            order.total_price = 0

        order.save()
        order_item.delete()

        order_items = Order_Item.objects.filter(order=order)
        serializer = OrderItemSerializer(order_items, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'PUT':
        product = get_object_or_404(Product, id=item_id)

        if product.stock_applies:
            if product.stock < 1 and not get_can_negative_stock():
                return JsonResponse('{message: "Insufficient stock"}',
                                    status=status.HTTP_400_BAD_REQUEST)

            product.stock -= 1
            product.save()

        Order_Item.objects.create(order=order, product=product,
                                  price=product.price, name=product.name)
        order.total_price = (
            decimal.Decimal(
                product.price) +
            order.total_price) \
            .quantize(decimal.Decimal('0.01'))
        order.save()

        order_items = Order_Item.objects.filter(order=order)
        serializer = OrderItemSerializer(order_items, many=True)
        return JsonResponse(serializer.data, safe=False)

    else:
        return HttpResponseBadRequest()


def cash_payment(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    order = get_current_user_order(request.user.username)
    cash, _ = Cash.objects.get_or_create(id=0)

    amount_added = 0

    for product in product_list_from_order(order):
        cash.amount += product.price
        amount_added += product.price
        cash.save()

    order.done = True
    order.save()
    Order.objects.create(user=request.user)

    return JsonResponse({'added': amount_added})


def card_payment(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    order = get_current_user_order(request.user.username)

    order.done = True
    order.save()
    Order.objects.create(user=request.user)

    return HttpResponse()
