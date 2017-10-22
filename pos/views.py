import logging
import decimal
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest
from django.template import loader
from django.core.exceptions import MultipleObjectsReturned
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from .models import Product, Order, ProductInOrder, Cash
from . import helper


def index(request):
    return HttpResponse("Hello World. This is the pos starting page")

def login(request):
    if request.method == "GET":
        if 'next' in request.GET:
            next = request.GET['next']
        else:
            next = 'pos/'

        context = {
            'error': False,
            'next': next
        }
        return render(request, 'registration/login.html', context=context)

    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)

    if user is not None:
        auth_login(request, user)
        if 'next' in request.GET:
            next = request.GET['next']
        else:
            next = '/pos/'
        return redirect(next)
    else:
        context = {
            'error': True
        }
        return render(request, 'registration/login.html', context=context)


@login_required
def order(request):
    product_list = Product.objects.all
    context = {
            'product_list': product_list,
    }
    return render(request, 'pos/order.html', context=context)


@login_required
def addition(request, operation):
    cash, _ = Cash.objects.get_or_create(id=0)
    succesfully_payed = False
    payment_error = False
    amount_added = 0
    q = Order.objects.filter(user=request.user, done=False)
    
    if q.count() >= 1:
        order = q[0]
    else:
        order = Order.objects.create(user=request.user)

    if operation:
        if operation.isdecimal():
            product = Product.objects.get(id=operation)
            pio = ProductInOrder(order=order, product=product)
            pio.save()
            order.total += product.price
            order.save()

        elif operation == "reset":
            order.products.clear()
            order.total = 0
            order.save()

        elif operation == "cashpayment" or operation == "cardpayment":
            # when a customer just paid in cash
            for product in order.products.all():
                if product.stockApplies:
                    product.stock -= 1
                    product.save()
                if operation == "cashpayment":
                    cash.cash_amount += product.price
                    amount_added += product.price
                    cash.save()

            order.done = True
            order.save()
            order = Order.objects.create(user=request.user)
            succesfully_payed = True

    context = {
            'order_list': order.productinorder_set.all(),
            'totalprice': order.total,
            'cash': cash,
            'succesfully_payed': succesfully_payed,
            'payment_error': payment_error,
            'amount_added': amount_added,
    }
    return render(request, 'pos/addition.html', context=context)


@login_required
def remove_from_order(request, order_id=None, pio_id=None):
    """Remove a specific item from the order"""

    # attempt ?pio_id= paramter if it was not in the url
    if pio_id is None: pio_id = request.GET.get('pio_id', None)

    pio = get_object_or_404(ProductInOrder, id=pio_id)
    #sanity check order id if it matches, sth was weird with the url otherwise
    if order_id is not None and (int(order_id) != pio.order.id):
        #product was not found!
        messages.add_message(request, messages.WARNING,
                    'Failed to find product \'\', nothing removed from the '
                    'order.')
        return HttpResponseBadRequest("Order id and Produkt id combination is impossible. This URL is misconstructed.")

    order = pio.order
    product = pio.product
    order.total -= product.price
    order.save()        

    if order.total < 0:
        logging.warn("prices below 0! You might be running in to the 10 digit total order price limit")
        order.total = 0
        order.save()
    
    pio.delete()
    context = {
            'order_list': order.productinorder_set.all(),
            'totalprice': order.total,
            'cash': cash,
    }
    return render(request, 'pos/addition.html', context=context)


def cash(request, amount):
    cash, _ = Cash.objects.get_or_create(id=0)
    cash.cash_amount = amount
    cash.save()
    return HttpResponse('')
