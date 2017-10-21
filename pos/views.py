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
    amount_added = 0
    q = Order.objects.filter(order_user=request.user.username, order_done=False).order_by('order_lastChange')
    if q.count() >= 1:
        current_order = q[0]
    else:
        current_order = Order.objects.create(order_user=request.user.username)

    if operation:
        if operation.isdecimal():
            current_order_parsed_list = helper.parse_json_product_list(current_order.order_list)
            product_to_add = Product.objects.get(product_id=operation)
            current_order_parsed_list.append(product_to_add)
            current_order.order_list = helper.product_list_to_json(current_order_parsed_list)
            current_order.order_totalprice = ( decimal.Decimal(product_to_add.product_price) + current_order.order_totalprice ).quantize(decimal.Decimal('0.01'))
            current_order.save()

        elif operation == "reset":
            current_order.order_list = "[]"
            current_order.order_totalprice = 0
            current_order.save()

        elif operation == "cashpayment":
            # when a customer just paid in cash
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

        elif operation == "cardpayment":
            for product in helper.parse_json_product_list(current_order.order_list):
                product_in_database = Product.objects.get(product_name=product.product_name)
                amount_added = amount_added + product.product_price
                if product_in_database.product_stockApplies:
                    product_in_database.product_stock = productInDatabase.product_stock - 1
                    product_in_database.save()

            current_order.order_done = True
            current_order.save()
            current_order = Order.objects.create(order_user=request.user.username)
            succesfully_payed = True



        else:
            product_in_database = Product.objects.filter(product_name = operation).first()
            if product_in_database is not None:
                parsed_json_list = helper.parse_json_product_list(current_order.order_list)

                i = parsed_json_list.index(product_in_database)
                del parsed_json_list[i]
                current_order.order_list = helper.product_list_to_json(parsed_json_list)
                current_order.order_totalprice = ( current_order.order_totalprice - product_in_database.product_price ).quantize(decimal.Decimal('0.01'))

                if current_order.order_totalprice < 0:
                    logging.warn("prices below 0! You might be running in to the 10 digit total order price limit")
                    current_order.order_totalprice = 0
                current_order.save()

    totalprice = current_order.order_totalprice
    order_list = helper.parse_json_product_list(current_order.order_list)
    template = loader.get_template('pos/addition.html')
    context = {
            'order_list': order_list,
            'totalprice': totalprice,
            'cash': cash,
            'succesfully_payed': succesfully_payed,
            'payment_error': payment_error,
            'amount_added': amount_added,
    }
    return HttpResponse(template.render(context, request))

def cash(request, amount):
    cash, _ = Cash.objects.get_or_create(id=0)
    cash.cash_amount = amount
    cash.save()
    return HttpResponse('')
