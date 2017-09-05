import logging
import decimal
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.core.exceptions import MultipleObjectsReturned
from django.contrib.auth.decorators import login_required
from .models import Product, Order, Cash
from . import helper

# Create your views here.
def index(request):
    return HttpResponse("Hello World. This is the pos starting page")

@login_required
def order(request):
    product_list = Product.objects.all
    template = loader.get_template('pos/order.html')
    context = {
            'product_list': product_list,
    }
    return HttpResponse(template.render(context, request))

def addition(request, operation):
    cash, _ = Cash.objects.get_or_create(id=0)
    succesfully_payed = False
    payment_error = False
    amountAdded = 0
    try:
        currentOrder, _ = Order.objects.get_or_create(order_user=request.user.username)
    except MultipleObjectsReturned:
        currentOrder = list(Order.objects.filter(order_user=request.user.username))[0]
        logging.warn("there were MultipleObjectsReturned")

    if currentOrder is None:
        raise Exception("currentOrder is empty")
    if operation:
        if operation.isdecimal():
            tmplist = helper.parseJsonProductList(currentOrder.order_list)
            tmpproduct = Product.objects.get(product_id=operation)
            tmplist.append(tmpproduct)
            currentOrder.order_list = helper.productListToJson(tmplist)
            currentOrder.order_totalprice = decimal.Decimal(tmpproduct.product_price) + currentOrder.order_totalprice
            currentOrder.save()
        elif operation == "reset":
            currentOrder.order_list = "[]"
            currentOrder.order_totalprice = 0
            currentOrder.save()
        elif operation == "payed":
            for product in helper.parseJsonProductList(currentOrder.order_list):
                productInDatabase = Product.objects.get(product_name=product.product_name)
                if productInDatabase.product_stockApplies:
                    productInDatabase.product_stock = productInDatabase.product_stock - 1
                productInDatabase.save()
                cash.cash_amount = cash.cash_amount + product.product_price
                amountAdded = amountAdded + product.product_price
                cash.save()
            currentOrder.order_list = "[]"
            currentOrder.order_totalprice = 0
            currentOrder.save()
            succesfully_payed = True
        else:
            tmpproduct = Product.objects.filter(product_name = operation).first()
            if tmpproduct is not None:
                tmplist = helper.parseJsonProductList(currentOrder.order_list)
                i = tmplist.index(tmpproduct)
                del tmplist[i]
                currentOrder.order_list = helper.productListToJson(tmplist)
                currentOrder.order_totalprice = currentOrder.order_totalprice - tmpproduct.product_price
                if currentOrder.order_totalprice < 0:
                    logging.warn("prices below 0! You might be running in to the 10 digit total order price limit")
                    currentOrder.order_totalprice = 0
                currentOrder.save()

    totalprice = currentOrder.order_totalprice
    order_list = helper.parseJsonProductList(currentOrder.order_list)
    template = loader.get_template('pos/addition.html')
    context = {
            'order_list': order_list,
            'totalprice': totalprice,
            'cash': cash,
            'succesfully_payed': succesfully_payed,
            'payment_error': payment_error,
            'amount_added': amountAdded,
    }
    return HttpResponse(template.render(context, request))
