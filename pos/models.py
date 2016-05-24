from django.db import models

# Create your models here.
class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=100)
    product_price = models.DecimalField(max_digits=7,decimal_places=3)
    product_stockApplies = models.BooleanField()
    product_stock = models.PositiveSmallIntegerField()

    def __str__(self):
        return product_name



#class User(models.Model):
#    user_id = models.AutoField(primary_key = True)
#    user_name = models.CharField(max_length=50)
#    user_isAdmin = models.BooleanField()
#
#    def __str__(self):
#        return user_name
#

