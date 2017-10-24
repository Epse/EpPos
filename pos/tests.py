from django.contrib.auth.models import User
from django.test import SimpleTestCase, Client, TransactionTestCase
from django.core.urlresolvers import reverse
from decimal import *
from .helper import parse_json_product_list, product_list_to_json
from .models import Product, Cash

class HelperTestCase(SimpleTestCase):
    product_list = []
    def setUp(self):
        self.product_list.append(Product(product_stockApplies = False, product_name="one", product_price=Decimal(12)))
        self.product_list.append(Product(product_stockApplies = False, product_name="two", product_price=Decimal(4)))
        self.product_list.append(Product(product_stockApplies = False, product_name="three", product_price=Decimal(0)))
        self.product_list.append(Product(product_stockApplies = False, product_name="four", product_price=Decimal(5000)))

    def test_json_parsing(self):
        json = product_list_to_json(self.product_list)
        test_list = parse_json_product_list(json)

        self.assertEqual(len(test_list), len(self.product_list))
        # The Decimal is necessary due to some Django magic
        for i in range(0, len(test_list)):
            self.assertEqual(test_list[i].product_price, Decimal(self.product_list[i].product_price))
            self.assertEqual(test_list[i].product_name, self.product_list[i].product_name)

class CashViewTestCase(TransactionTestCase):
    def test_cash_set(self):
        client = Client()
        response = client.get(reverse('cash', args=[5]))
        self.assertEqual(response.status_code, 200)

        cash, _ = Cash.objects.get_or_create(id=0)
        self.assertEqual(cash.cash_amount, 5)

    def test_cash_reset(self):
        cash, _ = Cash.objects.get_or_create(id=0)
        cash.cash_amount = 5
        cash.save()

        client = Client()
        response = client.get(reverse('cash', args=[0]))
        self.assertEqual(response.status_code, 200)

        cash, _ = Cash.objects.get_or_create(id=0)
        self.assertEqual(cash.cash_amount, 0)

class OrderViewTestCase(TransactionTestCase):
    product_list = []
    def setUp(self):
        self.client = Client()
        self.product_list.append(Product.objects.create(product_stockApplies = False, product_name="one", product_price=Decimal(12)))
        self.product_list.append(Product.objects.create(product_stockApplies = False, product_name="two", product_price=Decimal(4)))
        self.product_list.append(Product.objects.create(product_stockApplies = False, product_name="three", product_price=Decimal(0)))
        self.product_list.append(Product.objects.create(product_stockApplies = False, product_name="four", product_price=Decimal(5000)))

        self.user = User.objects.create_user('test', 'test@example.com', 'pswd')

    def test_view(self):
        # The Order view has the `@login_required` decorator
        self.client.login(username='test', password='pswd')

        response = self.client.get(reverse('order'))
        self.assertEqual(response.status_code, 200)

        response_product_list = response.context['product_list']()

        self.assertEqual(len(response_product_list), len(self.product_list))

        for i in range(0, len(response_product_list)):
            self.assertEqual(response_product_list[i].product_name, self.product_list[i].product_name)
            self.assertEqual(response_product_list[i].product_price, self.product_list[i].product_price)
