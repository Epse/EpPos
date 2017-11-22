import logging
import decimal
from django.shortcuts import render, get_object_or_404
from django.http import (HttpResponse,
                         HttpResponseForbidden,
                         HttpResponseBadRequest)
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from .models import Product, Order, Cash, Order_Item
from . import helper


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
    list = Product.objects.all
    context = {
            'list': list,
    }
    return render(request, 'pos/order.html', context=context)


@login_required
def addition(request):
    cash, current_order = helper.setup_handling(request)

    total_price = current_order.total_price
    list = Order_Item.objects.filter(order=current_order)
    print(list)
    context = {
            'list': list,
            'total_price': total_price,
            'cash': cash,
            'succesfully_payed': False,
            'payment_error': False,
            'amount_added': 0,
    }
    return render(request, 'pos/addition.html', context=context)


@login_required
def order_add_product(request, product_id):
    cash, current_order = helper.setup_handling(request)

    to_add = get_object_or_404(Product, id=product_id)
    Order_Item.objects.create(order=current_order, product=to_add,
                              price=to_add.price, name=to_add.name)
    current_order.total_price = (
        decimal.Decimal(
            to_add.price) +
        current_order.total_price) \
        .quantize(decimal.Decimal('0.01'))
    current_order.save()

    return addition(request)


@login_required
def order_remove_product(request, product_id):
    cash, current_order = helper.setup_handling(request)
    order_product = get_object_or_404(Order_Item, id=product_id)

    current_order.total_price = (
        current_order.total_price -
        order_product.price).quantize(
            decimal.Decimal('0.01'))

    if current_order.total_price < 0:
        logging.error("prices below 0! "
                      "You might be running in to the "
                      "10 digit total order price limit")
        current_order.total_price = 0

    current_order.save()
    order_product.delete()

    # I only need default values.
    return addition(request)


@login_required
def reset_order(request):
    cash, current_order = helper.setup_handling(request)
    current_order.list = "[]"
    current_order.total_price = 0
    current_order.save()

    # I just need default values. Quite useful
    return addition(request)


@login_required
def payment_cash(request):
    succesfully_payed = False
    payment_error = False
    amount_added = 0
    cash, current_order = helper.setup_handling(request)

    for ordered_product in helper\
            .parse_json_list(current_order.list):
        product = Product.objects.get(
            name=ordered_product.name)
        if product.stock_applies:
            product.stock -= 1
            product.save()

        cash.amount += ordered_product.price
        amount_added += ordered_product.price
        cash.save()

    current_order.done = True
    current_order.save()
    current_order = Order.objects.create(user=request.user.username)
    succesfully_payed = True

    total_price = current_order.total_price
    list = helper.parse_json_list(current_order.list)
    context = {
            'list': list,
            'total_price': total_price,
            'cash': cash,
            'succesfully_payed': succesfully_payed,
            'payment_error': payment_error,
            'amount_added': amount_added,
    }
    return render(request, 'pos/addition.html', context=context)


@login_required
def payment_card(request):
    succesfully_payed = False
    payment_error = False
    cash, current_order = helper.setup_handling(request)

    for product in helper.parse_json_list(current_order.list):
        in_database = Product\
                              .objects\
                              .get(name=product.name)
        if in_database.stock_applies:
            in_database.stock -= 1
            in_database.save()

        current_order.done = True
        current_order.save()
        current_order = Order.objects.create(user=request.user.username)
        succesfully_payed = True

    total_price = current_order.total_price
    list = helper.parse_json_list(current_order.list)
    context = {
            'list': list,
            'total_price': total_price,
            'cash': cash,
            'succesfully_payed': succesfully_payed,
            'payment_error': payment_error,
            'amount_added': 0,
    }
    return render(request, 'pos/addition.html', context=context)


# We can't use the `@login_required` decorator here because this
# page is never shown to the user and only used in AJAX requests
def cash(request, amount):
    if (request.user.is_authenticated):
        cash, _ = Cash.objects.get_or_create(id=0)
        cash.amount = amount
        cash.save()
        return HttpResponse('')
    else:
        return HttpResponseForbidden('403 Forbidden')
