from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
import logging
import json
import re

def validate_product_name(prodname):
    regex_string = r'^[\w ]+$'
    search = re.compile(regex_string).search
    result = bool(search(prodname))
    if not result:
        raise ValidationError("Please only use letters, numbers and underscores.")

# Create your models here.
class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, validators=[validate_product_name],
                            help_text="Title for the product")
    price = models.DecimalField(max_digits=7,decimal_places=2,
                                help_text="Gross price per item")
    stockApplies = models.BooleanField(default=False,
                                       help_text="Does selling an item reduce "
                                       "the number on stock?")
    stock = models.PositiveSmallIntegerField(default=0,
                                             help_text="The number of items on"
                                             " stock")

    def __str__(self):
        return self.name

    def clean(self):
        validate_product_name(self.name)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.full_clean()
        super(Product, self).save(*args, **kwargs)

    def to_json(self):
        return json.dumps(self.__jsonDict__)

    def from_json(json):
        jsonDict = json.loads(json)
        self.id = jsonDict['id']
        self.name = jsonDict['name']
        self.price = jsonDict['price']
        self.stockApplies = jsonDict['stockApplies']
        self.stock = jsonDict['stock']

    class Meta:
        ordering = ['name']
        default_related_name = 'products'


class Order(models.Model):
    """Representing a single order for which a seller is responsible"""
    # user is the waiter/seller of this order
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             help_text="The seller/waiter handling this "
                             "order.")
    # contains a list of products in this order
    products = models.ManyToManyField(Product, through='ProductInOrder',
                                      help_text="A list of products "
                                      "comprising the order.")
    # contains the total order amonut
    total = models.DecimalField(max_digits=10,decimal_places=2,default=0,
                                editable=False,
                                help_text="Total amount of the order.")
    # True if the order was handled and paid
    done = models.BooleanField(default=False,
                               help_text="Has the order been handled and "
                               "paid?")
    # updated when the order changes
    lastChange = models.DateTimeField(auto_now=True,
                                      help_text="Last modification time.")
    # when the order started (to allow creating stats, group by day,...)
    # For backward compatibility we need to allow None as startDate for
    # orders before this field was introduced
    startTime = models.DateTimeField(auto_now_add=True, editable=False,
                                     null=True, blank=True,
                                     help_text="Order was created at this "
                                     "time.")

    def __str__(self):              # __unicode__ on Python 2
        return "Order #{} ({})".format(self.id, self.user)

    class Meta:
        ordering = ['-lastChange']
        get_latest_by = "lastChange"


class ProductInOrder(models.Model):
    """Intermediary model connecting products and orders"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

                    
class Cash(models.Model):
    cash_amount = models.DecimalField(max_digits=7, decimal_places=2,default=0)
