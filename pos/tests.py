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
        # The Decimal is necessary due to some Django magic
        self.assertEqual(test_list[0].product_price, Decimal(self.product_list[0].product_price))
        self.assertEqual(test_list[1].product_price, Decimal(self.product_list[1].product_price))
        self.assertEqual(test_list[2].product_price, Decimal(self.product_list[2].product_price))
        self.assertEqual(test_list[3].product_price, Decimal(self.product_list[3].product_price))

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
