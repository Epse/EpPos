from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
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
    currentOrder = Order.objects.filter(order_user=request.user.username)[:1]
    order_list = currentOrder.getList()
    product_list = Product.objects.all

    if operation:
        if operation.isdecimal():
            #Find the product name for this ID
            for x in product_list:
                if x.product_id == operation:
                    current_product = x

            order_list.append(current_product)
            currentOrder.setList(order_list)
            currentOrder.save()
        else:
            if operation == "reset":
                currentOrder.setList([])
                currentOrder.save()
            elif operation == "payed":
                #TODO: this should add the received money, for now it is equal to reset
                currentOrder.setList([])
                currentOrder.save()

    template = loader.get_template('pos/addition.html')
    context = {
            'order_list': order_list
    }
    return HttpResponse(template.render(context, request))

