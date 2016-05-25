from django.db import models
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

    def setList(self, x):
        self.order_list = json.dumps(x)

    def getList(self):
        return json.loads(self.order_list)


#class User(models.Model):
#    user_id = models.AutoField(primary_key = True)
#    user_name = models.CharField(max_length=50)
#    user_isAdmin = models.BooleanField()
#
#    def __str__(self):
#        return user_name
#

