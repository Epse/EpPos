import logging
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.core.exceptions import MultipleObjectsReturned
from django.contrib.auth.decorators import login_required
import json
from .models import Product, Order

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
    try:
        currentOrder,_ = Order.objects.get_or_create(order_user=request.user.username)
    except MultipleObjectsReturned:
        currentOrder = list(Order.objects.filter(order_user=request.user.username))[0]
        logging.warn("there were MultipleObjectsReturned")

    if currentOrder is None:
        raise Exception("currentOrder is empty")
    if operation:
        if operation.isdecimal():
            tmplist = json.loads(currentOrder.order_list)
            tmpproduct = Product.objects.get(product_id=operation)
            tmplist.append(tmpproduct.product_name)
            currentOrder.order_list = json.dumps(tmplist)
            currentOrder.order_totalprice = tmpproduct.product_price + currentOrder.order_totalprice
            currentOrder.save()
        elif operation == "reset":
            currentOrder.order_list = json.dumps(list())
            currentOrder.order_totalprice = 0
            currentOrder.save()
        elif operation == "payed":
            #TODO: this should add the received money, for now it is equal to reset
            currentOrder.order_list = json.dumps(list())
            currentOrder.order_totalprice = 0
            currentOrder.save()
        else:
            tmpproduct = Product.objects.filter(product_name = operation).first()
            if tmpproduct is not None:
                tmplist = json.loads(currentOrder.order_list)
                i = tmplist.index(tmpproduct.product_name) 
                del tmplist[i]
                currentOrder.order_list = json.dumps(tmplist)
                currentOrder.order_totalprice = currentOrder.order_totalprice - tmpproduct.product_price
                if currentOrder.order_totalprice < 0:
                    logging.warn("prices below 0!")
                    currentOrder.order_totalprice = 0
                currentOrder.save()

    totalprice = currentOrder.order_totalprice
    order_list = json.loads(currentOrder.order_list)
    template = loader.get_template('pos/addition.html')
    context = {
            'order_list': order_list,
            'totalprice': totalprice,
    }
    return HttpResponse(template.render(context, request))

