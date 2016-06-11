from django.db import models
from django.core.exceptions import ValidationError
import logging
import json

def validate_product_name(prodname):
    regex_string = r'^([A-Za-z0-9\.\+\(\)\-\_])+$'
    if regex.match(regex_string, prodname) == None:
        raise ValidationError("Please only use letters, numbers and .+()-_ symbols.")


# Create your models here.
class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=100, validators=[validate_product_name])
    product_price = models.DecimalField(max_digits=7,decimal_places=3)
    product_stockApplies = models.BooleanField()
    product_stock = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.product_name

class Order(models.Model):
    order_user = models.CharField(max_length=50)
    order_list = models.CharField(max_length=1000)
    order_totalprice = models.DecimalField(max_digits=7,decimal_places=3,default=0)

class Cash(models.Model):
    cash_amount = models.DecimalField(max_digits=7, decimal_places=3,default=0)
