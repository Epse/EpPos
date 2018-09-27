from django.contrib.auth.models import User
from .models import Order, Cash, Order_Item, Setting


def get_currency():
    """
    Gets the current currency from the Settings database table
    """

    currency, is_created = Setting.objects.get_or_create(key="currency")

    if is_created:
        currency.value = "€"
        currency.save()

    return currency.value


def get_company():
    """
    Gets the company name from the Settings in the database
    """

    company, is_created = Setting.objects.get_or_create(key="company")

    if is_created:
        company.value = "EpPos"
        company.save()

    return company.value


def get_can_negative_stock():
    """
    Gets from database if negative stock is allowed. Returns True when allowed.
    """

    setting, is_created = Setting.objects.get_or_create(key="negative_stock")

    if is_created:
        setting.value = "off"
        setting.save()
        return False

    print(setting.value)
    if setting.value == "off" or setting.value == "no":
        return False
    return True


def setup_handling(request):
    """
    Boilerplate that gets the Cash, current order and currency.
    """

    cash, _ = Cash.objects.get_or_create(id=0)
    current_order = get_current_user_order(request.user.username)
    currency = get_currency()

    return (cash, current_order, currency)


def get_current_user_order(username):
    """
    Gets the order for the current user.
    """

    usr = User.objects.get_by_natural_key(username)
    q = Order.objects.filter(user=usr, done=False)\
                     .order_by('-last_change')
    if q.count() >= 1:
        return q[0]
    else:
        return Order.objects.create(user=usr)


def order_item_from_product(product, order):
    """
    Creates an Order-Item from a given Product,
    to be added to an Order.
    """

    return Order_Item.objects.create(product=product,
                                     order=order,
                                     price=product.price,
                                     name=product.name)


def product_list_from_order(order):
    """
    Returns a list of Products that appear in an Order
    """

    product_list = []
    order_item_list = Order_Item.objects.filter(order=order)

    for order_item in order_item_list:
        product_list.append(order_item.product)

    return product_list
