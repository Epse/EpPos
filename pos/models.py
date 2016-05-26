from django.db import models
import logging
import json

# Create your models here.
class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=100)
    product_price = models.DecimalField(max_digits=7,decimal_places=3)
    product_stockApplies = models.BooleanField()
    product_stock = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.product_name

class Order(models.Model):
    order_user = models.CharField(max_length=50)
    order_list = models.CharField(max_length=1000)
    order_totalprice = models.PositiveSmallIntegerField(default=0)

    def setList(self, x):
        self.order_list = json.dumps(x)
        self.save()

    def getList(self):
        return json.loads(self.order_list)

    def appendProduct(self, productID):
        for product in Product.objects.all():
            if product.product_id == productID:
                currentProduct = product
        orderlist = json.loads(self.order_list)
        orderlist.append(product.product_name)
        jsonorder = json.dumps(orderlist)
        self.order_list = jsonorder
        self.order_totalprice += product.product_price
        self.save()
        
    def removeProduct(self, productName):
        for product in Product.objects.all():
            if product.product_name == productName:
                currentProduct = product
        currindex = self.order_list.index(product.product_name)
        del self.order_list[currindex]
        self.order_totalprice -= product.product_price
        self.save()

    def clearList(self):
        self.order_list = json.dumps(list())
        self.order_totalprice = 0
        self.save()

#class User(models.Model):
#    user_id = models.AutoField(primary_key = True)
#    user_name = models.CharField(max_length=50)
#    user_isAdmin = models.BooleanField()
#
#    def __str__(self):
#        return user_name
#

