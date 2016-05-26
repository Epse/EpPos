import logging
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.core.exceptions import MultipleObjectsReturned
import json
from .models import Product, Order

# Create your views here.
def index(request):
    return HttpResponse("Hello World. This is the pos starting page")

def order(request):
    product_list = Product.objects.all
    template = loader.get_template('pos/order.html')
    context = {
            'product_list': product_list,
    }
    return HttpResponse(template.render(context, request))

def addition(request, operation):
    logging.info(request.user.username)
    try:
        currentOrder,_ = Order.objects.get_or_create(order_user=request.user.username,order_list=json.dumps(list()))
    except MultipleObjectsReturned:
        currentOrder = list(Order.objects.filter(order_user=request.user.username))[0]

    if operation:
        if operation.isdecimal():
            #Find the product name for this ID
            logging.warn("adding no: " + str(operation))
            for x in Product.objects.all():
                if x.product_id == operation:
                    current_product = x

            currentOrder.appendProduct(x.product_id)
        else:
            if operation == "reset":
                currentOrder.clearList()
            elif operation == "payed":
                #TODO: this should add the received money, for now it is equal to reset
                currentOrder.clearList()

    totalprice = currentOrder.order_totalprice
    order_list = currentOrder.getList()
    template = loader.get_template('pos/addition.html')
    context = {
            'order_list': order_list,
            'totalprice': totalprice,
    }
    return HttpResponse(template.render(context, request))

