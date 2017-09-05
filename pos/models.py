from django.db import models
from django.core.exceptions import ValidationError
import logging
import json
import re

def validate_product_name(prodname):
    regex_string = r'^\w+$'
    search = re.compile(regex_string).search
    result = bool(search(prodname))
    if not result:
        raise ValidationError("Please only use letters, numbers and underscores.")

# Create your models here.
class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=100, validators=[validate_product_name])
    product_price = models.DecimalField(max_digits=7,decimal_places=3)
    product_stockApplies = models.BooleanField()
    product_stock = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.product_name

    def clean(self):
        validate_product_name(self.product_name)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.full_clean()
        super(Product, self).save(*args, **kwargs)

    def toJson(self):
        return json.dumps(self.__jsonDict__)

    def fromJson(json):
        jsonDict = json.loads(json)
        self.product_id = jsonDict['product_id']
        self.product_name = jsonDict['product_name']
        self.product_price = jsonDict['product_price']
        self.product_stockApplies = jsonDict['product_stockApplies']
        self.product_stock = jsonDict['product_stock']

class Order(models.Model):
    order_user = models.CharField(max_length=50)
    order_list = models.CharField(max_length=10000, default="[]")
    order_totalprice = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    order_done = models.BooleanField(default=False)
    order_lastChange = models.DateField(auto_now=True)

class Cash(models.Model):
    cash_amount = models.DecimalField(max_digits=7, decimal_places=2,default=0)
