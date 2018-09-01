from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from decimal import Decimal
from . import helper
from .models import Order, Product, Cash, validate_product_name, Order_Item


def _helper():
    list = []
    product_list = []

    user = User.objects.create_user(
        'test', 'test@example.com', 'pswd')
    order = Order.objects.create(
        user=user,
        total_price=0,
        done=False)

    price = 0

    for i in range(4):
        prod = Product.objects.create(
            stock_applies=False,
            name=str(i),
            price=Decimal(3*i))
        product_list.append(prod)
        list.append(helper.order_item_from_product(prod, order))
        price += 3*i

    order.total_price = Decimal(price)
    order.save()

    return user, list, product_list


class CashViewTestCase(TestCase):
    def setUp(self):
        self.user, _, _ = _helper()

    def test_set(self):
        self.client.login(username='test', password='pswd')
        response = self.client.get(reverse('cash', args=[5]))
        self.assertEqual(response.status_code, 200)

        cash, _ = Cash.objects.get_or_create(id=0)
        self.assertEqual(cash.amount, 5)

    def test_reset(self):
        cash, _ = Cash.objects.get_or_create(id=0)
        cash.amount = 5
        cash.save()

        self.client.login(username='test', password='pswd')
        response = self.client.get(reverse('cash', args=[0]))
        self.assertEqual(response.status_code, 200)

        cash, _ = Cash.objects.get_or_create(id=0)
        self.assertEqual(cash.amount, 0)

    def test_not_logged_in(self):
        self.client.logout()
        response = self.client.get(reverse('cash', args=[0]))
        self.assertEqual(response.status_code, 403)


class OrderViewTestCase(TestCase):
    list = []

    def setUp(self):
        self.user, self.list, _ = _helper()

    def test_view(self):
        # The Order view has the `@login_required` decorator
        self.client.login(username='test', password='pswd')

        response = self.client.get(reverse('order'))
        self.assertEqual(response.status_code, 200)

        response_list = response.context['list']()

        self.assertEqual(len(response_list), len(self.list))

        for i in range(0, len(response_list)):
            self.assertEqual(response_list[i].name,
                             self.list[i].name)
            self.assertEqual(response_list[i].price,
                             self.list[i].price)


class ProductNameTestCase(TestCase):
    test_names_correct = []
    test_names_incorrect = []

    def setUp(self):
        self.test_names_correct.append('ProductOne')
        self.test_names_correct.append('Product Two')
        self.test_names_correct.append('3')
        self.test_names_correct.append('prodUct_four')

        self.test_names_incorrect.append(' ')
        self.test_names_incorrect.append('')
        self.test_names_incorrect.append(' One_2 3')
        self.test_names_incorrect.append('product-one')

    def test_correct_names(self):
        for name in self.test_names_correct:
            # Self might seem dodgy, but if it raises an error,
            # that will count as a failed test.
            validate_product_name(name)

    def test_incorrect_names(self):
        for name in self.test_names_incorrect:
            self.assertRaises(ValidationError, validate_product_name, name)


class OrderTestCase(TestCase):
    list = []
    initial_amount = 15

    def setUp(self):
        self.user, _, self.list = _helper()

        # Set some initial cash amount
        cash, _ = Cash.objects.get_or_create(id=0)
        cash.amount = self.initial_amount
        cash.save()

    def creation_helper(self):
        self.client.login(username='test', password='pswd')

        # Add things to basket and while we're at it, calculate the total price
        price = helper.get_current_user_order(self.user.username).total_price
        for product in self.list:
            response = self.client.get(reverse('order_add_product',
                                               args=[product.id]))
            self.assertEqual(response.status_code, 200)
            price += product.price

        order = helper.get_current_user_order(self.user.username)
        self.assertEqual(order.total_price, price)
        return price

    def test_card_payment(self):
        self.creation_helper()

        # Now pay by card
        response = self.client.get(reverse('payment_card'))
        self.assertEqual(response.status_code, 200)

        # Check if order is reset
        order = helper.get_current_user_order(self.user.username)
        self.assertEqual(order.total_price, 0)

        # Just to be sure, amount is not added to cash
        cash, _ = Cash.objects.get_or_create(id=0)
        self.assertEqual(cash.amount, self.initial_amount)

    def test_cash_payment(self):
        price = self.creation_helper()

        # Now pay by cash
        response = self.client.get(reverse('payment_cash'))
        self.assertEqual(response.status_code, 200)

        # Check if order is reset
        order = helper.get_current_user_order(self.user.username)
        self.assertEqual(order.total_price, 0)

        # Check if amount added to cash
        cash, _ = Cash.objects.get_or_create(id=0)
        self.assertEqual(cash.amount, price + self.initial_amount)


class OrderManagementTestCase(TestCase):
    list = []

    def setUp(self):
        self.user, _, self.list = _helper()
        self.client.login(username='test', password='pswd')

    def test_add_to_order(self):
        response = self.client.get(reverse('order_add_product',
                                           args=[self.list[0].id]))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('order_add_product', args=['100']))
        self.assertEqual(response.status_code, 404)

    def test_order_reset(self):
        response = self.client.get(reverse('reset_order'))
        self.assertEqual(response.status_code, 200)

        order = helper.get_current_user_order(self.user.username)
        order_items = Order_Item.objects.filter(order=order)
        self.assertCountEqual(order_items, [])


class HelperTestCase(TestCase):
    list = []
    product_list = []

    def setUp(self):
        self.user, self.list, self.product_list = _helper()

    def test_product_list_from_order(self):
        order = helper.get_current_user_order(self.user.username)
        self.assertEqual(self.product_list,
                         helper.product_list_from_order(order))


class StockTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            'tester', 'test@example.com', 'pswd')
        self.client.login(username='tester', password='pswd')
        Product.objects.create(
            stock_applies=True,
            name="stocked",
            price=Decimal(5),
            stock=3)
        Product.objects.create(
            stock_applies=True,
            name="outofstock",
            price=Decimal(20),
            stock=0)
        Product.objects.create(
            stock_applies=False,
            name="nostock",
            price=Decimal(20))

    def test_order(self):
        # Any open orders can go.
        Order.objects.filter(user=self.user).delete()

        Order.objects.create(user=self.user,
                             total_price=0,
                             done=False)

        response = self.client.get(
            reverse("order_add_product",
                    args=[Product.objects.get(name="stocked").id]))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse("order_add_product",
                    args=[Product.objects.get(name="outofstock").id]))
        self.assertEqual(response.status_code, 400)

        response = self.client.get(
            reverse("order_add_product",
                    args=[Product.objects.get(name="nostock").id]))
        self.assertEqual(response.status_code, 200)

        # One item should have been reserved
        self.assertEqual(Product.objects.get(name="stocked").stock, 2)

        response = self.client.get(reverse("payment_card"))
        self.assertEqual(response.status_code, 200)

        # One item should have been sold
        self.assertEqual(Product.objects.get(name="stocked").stock, 2)

    def test_cancelled_order(self):
        # Any open orders can go.
        Order.objects.filter(user=self.user).delete()

        Order.objects.create(user=self.user,
                             total_price=0,
                             done=False)

        stocked = Product.objects.get(name="stocked").stock

        response = self.client.get(
            reverse("order_add_product",
                    args=[Product.objects.get(name="stocked").id]))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse("order_add_product",
                    args=[Product.objects.get(name="outofstock").id]))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Product.objects.get(name="outofstock").stock, 0)

        response = self.client.get(reverse("reset_order"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Product.objects.get(name="stocked").stock, stocked)
        self.assertEqual(Product.objects.get(name="outofstock").stock, 0)
