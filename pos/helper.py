import json
import decimal
from django.contrib.auth.models import User
from .models import Product, Order, Cash


def setup_handling(request):
    cash, _ = Cash.objects.get_or_create(id=0)
    current_order = get_current_user_order(request.user.username)

    return (cash, current_order)


def get_current_user_order(username):
    usr = User.objects.get_by_natural_key(username)
    q = Order.objects.filter(user=usr, done=False)\
                     .order_by('last_change')
    if q.count() >= 1:
        return q[0]
    else:
        return Order.objects.create(user=usr)
