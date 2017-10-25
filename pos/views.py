import logging
import decimal
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.template import loader
from django.core.exceptions import MultipleObjectsReturned
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from .models import Product, Order, Cash
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
    product_list = Product.objects.all
    context = {
            'product_list': product_list,
    }
    return render(request, 'pos/order.html', context=context)


@login_required
def addition(request):
    cash, current_order = helper.setup_order_handling(request)

    totalprice = current_order.order_totalprice
    order_list = helper.parse_json_product_list(current_order.order_list)
    context = {
            'order_list': order_list,
            'totalprice': totalprice,
            'cash': cash,
            'succesfully_payed': False,
            'payment_error': False,
            'amount_added': 0,
    }
    return render(request, 'pos/addition.html', context=context)


@login_required
def order_add_product(request, product_id):
    cash, current_order = helper.setup_order_handling(request)

    if not product_id.isdecimal():
        return HttpResponseBadRequest('BAD REQUEST\nproduct ID is not decimal')

    current_order_parsed_list = helper.parse_json_product_list(
        current_order.order_list)
    product_to_add = Product.objects.get(product_id=product_id)
    current_order_parsed_list.append(product_to_add)
    current_order.order_list = helper.product_list_to_json(
        current_order_parsed_list)
    current_order.order_totalprice = (
        decimal.Decimal(
            product_to_add.product_price) +
            current_order.order_totalprice) \
                 .quantize(decimal.Decimal('0.01'))
    current_order.save()

    return addition(request)


@login_required
def order_remove_product(request, product_name):
    cash, current_order = helper.setup_order_handling(request)
    product_in_database = Product.objects\
                                 .filter(product_name=product_name) \
                                 .first()
    if product_in_database is None:
        return HttpResponseBadRequest('BAD REQUEST: Product does not exist')

    parsed_json_list = helper\
                       .parse_json_product_list(
                           current_order.order_list)

    i = parsed_json_list.index(product_in_database)
    del parsed_json_list[i]
    current_order.order_list = helper\
                 .product_list_to_json(
                     parsed_json_list)
    current_order.order_totalprice = (
        current_order.order_totalprice -
        product_in_database.product_price)\
                 .quantize(decimal.Decimal('0.01'))

    if current_order.order_totalprice < 0:
        logging.error("prices below 0! You might be running in to the 10 digit total order price limit")
        current_order.order_totalprice = 0

    current_order.save()

    # I only need default values.
    return addition(request)


@login_required
def reset_order(request):
    cash, current_order = helper.setup_order_handling(request)
    current_order.order_list = "[]"
    current_order.order_totalprice = 0
    current_order.save()

    # I just need default values. Quite useful
    return addition(request)


@login_required
def payment_cash(request):
    succesfully_payed = False
    payment_error = False
    amount_added = 0
    cash, current_order = helper.setup_order_handling(request)

    for ordered_product in helper.parse_json_product_list(current_order.order_list):
        product = Product.objects.get(
            product_name=ordered_product.product_name)
        if product.product_stockApplies:
            product.product_stock -= 1
            product.save()

        cash.cash_amount += ordered_product.product_price
        amount_added += ordered_product.product_price
        cash.save()

    current_order.order_done = True
    current_order.save()
    current_order = Order.objects.create(order_user=request.user.username)
    succesfully_payed = True

    totalprice = current_order.order_totalprice
    order_list = helper.parse_json_product_list(current_order.order_list)
    context = {
            'order_list': order_list,
            'totalprice': totalprice,
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
    amount_added = 0
    cash, current_order = helper.setup_order_handling(request)

    for product in helper.parse_json_product_list(current_order.order_list):
        product_in_database = Product\
                              .objects\
                              .get(product_name=product.product_name)
        if product_in_database.product_stockApplies:
            product_in_database.product_stock -= 1
            product_in_database.save()

        current_order.order_done = True
        current_order.save()
        current_order = Order.objects.create(order_user=request.user.username)
        succesfully_payed = True

    totalprice = current_order.order_totalprice
    order_list = helper.parse_json_product_list(current_order.order_list)
    context = {
            'order_list': order_list,
            'totalprice': totalprice,
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
        cash.cash_amount = amount
        cash.save()
        return HttpResponse('')
    else:
        return HttpResponseForbidden('403 Forbidden')
