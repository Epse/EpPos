import json
import decimal
from .models import Product, Order


# Takes the standard JSON representation of these arrays
# and returns them as an actual array of Product
def parse_json_product_list(json_string):
    json_dict = json.loads(json_string)
    resulting_list = []

    for product_dict in json_dict:
        product = Product()
        product.product_id = product_dict['product_id']
        product.product_name = product_dict['product_name']
        # Turns the Number into a Decimal, than limits to two decimal places
        product.product_price = decimal.Decimal(product_dict['product_price']) \
                                       .quantize(decimal.Decimal('0.01'))
        product.product_stock = product_dict['product_stock']
        product.product_stockApplies = product_dict['product_stockApplies']
        resulting_list.append(product)

    return resulting_list


# This is bodgy...
# I have to do the array constructs manually because
# otherwise it would turn into an array of strings...
def product_list_to_json(product_list):
    json_string = "["

    for product in product_list:
        if json_string is not "[":
            json_string += ","

        clean_dict = product.__dict__
        # This state thing is a hidden Django object that
        # can't be serialized and doesn't need to be either
        del clean_dict['_state']
        clean_dict['product_price'] = str(clean_dict['product_price'])
        json_string += json.dumps(clean_dict)

    json_string += "]"

    return json_string

def setup_order_handling(request):
    cash, _ = Cash.objects.get_or_create(id=0)
    q = Order.objects.filter(order_user=request.user.username, order_done=False).order_by('order_lastChange')
    if q.count() >= 1:
        current_order = q[0]
    else:
        current_order = Order.objects.create(order_user=request.user.username)

    return (cash, current_order)

def get_current_user_order(username):
        return Order.objects.filter(order_user=username, order_done=False).order_by('order_lastChange')[0]
