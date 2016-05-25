from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .models import Product

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
    return HttpResponse("Hello. Here you will be able to see the order, as well as the due amount.\n operation is %s" %operation)

