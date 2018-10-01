import re
from django.db import models
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.conf import settings


def validate_product_name(prodname):
    regex_string = r'^\w[\w ]*$'
    search = re.compile(regex_string).search
    result = bool(search(prodname))
    if not result:
        raise ValidationError("Please only use letters, "
                              "numbers and underscores or spaces. "
                              "The name cannot start with a space.")


class Product(models.Model):
    # The different colours, to use as Product.<colour>
    BLUE = "blue"
    GREEN = "green"
    YELLOW = "yellow"
    ORANGE = "orange"
    PURPLE = "purple"
    BLACK = "black"
    PINK = "pink"
    CYAN = "cyan"

    # Colour choices
    COLOUR_CHOICES = (
            (BLUE, "Blue"),
            (GREEN, "Green"),
            (YELLOW, "Yellow"),
            (ORANGE, "Orange"),
            (PURPLE, "Purple"),
            (BLACK, "Black"),
            (PINK, "Pink"),
            (CYAN, "Cyan"),
    )

    name = models.CharField(max_length=100,
                            validators=[validate_product_name])
    price = models.DecimalField(max_digits=7, decimal_places=2)
    stock_applies = models.BooleanField()
    minimum_stock = models.PositiveSmallIntegerField(default=0)
    stock = models.IntegerField(default=0)
    code = models.CharField(max_length=50, unique=True, null=True, blank=True)
    colour = models.CharField(max_length=10,
                              choices=COLOUR_CHOICES, default="blue")

    def __str__(self):
        return self.name

    def clean(self):
        validate_product_name(self.name)
        if self.code == "":
            self.code = None

    def save(self, *args, **kwargs):
        if not self.pk:
            self.full_clean()
        return super(Product, self).save(*args, **kwargs)


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10,
                                      decimal_places=2,
                                      default=0)
    done = models.BooleanField(default=False)
    last_change = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('view_order', args=[self.id])


class Cash(models.Model):
    amount = models.DecimalField(max_digits=7,
                                 decimal_places=2,
                                 default=0)


class Order_Item(models.Model):
    product = models.ForeignKey(Product,
                                on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    name = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now=True)


class Setting(models.Model):
    key = models.CharField(max_length=50)
    value = models.CharField(max_length=100)

    def __str__(self):
        return self.key

    def __bool__(self):
        return bool(self.value)

    __nonzero__ = __bool__
