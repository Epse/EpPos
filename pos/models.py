from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
import re


def validate_product_name(prodname):
    regex_string = r'^\w[\w ]*$'
    search = re.compile(regex_string).search
    result = bool(search(prodname))
    if not result:
        raise ValidationError("Please only use letters, "
                              "numbers and underscores or spaces. "
                              "The name cannot start with a space.")


class Product(models.Model):
    name = models.CharField(max_length=100,
                            validators=[validate_product_name])
    price = models.DecimalField(max_digits=7, decimal_places=2)
    stock_applies = models.BooleanField()
    stock = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.name

    def clean(self):
        validate_product_name(self.name)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.full_clean()
        super(Product, self).save(*args, **kwargs)


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10,
                                      decimal_places=2,
                                      default=0)
    done = models.BooleanField(default=False)
    last_change = models.DateTimeField(auto_now=True)


class Cash(models.Model):
    amount = models.DecimalField(max_digits=7,
                                 decimal_places=2,
                                 default=0)


class Order_Item(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    name = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now=True)
