from django.contrib import admin
from .models import Product, Cash, Order, Setting

# Register your models here.
admin.site.register(Cash)

# Admin settings
admin.site.site_header = "EpPos Administration"
admin.site.site_title = "EpPos Administration"


# Admin Models
@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):

    # You really shouldn't add random settings
    def has_add_permission(self, request):
        return False

    # Deleting a setting seems odd...
    def has_delete_permission(self, *args, **kwargs):
        return False

    # List Display Page Configuration
    list_display = (
        'key',
        'value'
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    The Admin Configuration for the model Product.
    """

    # List Page Display Configuration
    list_display = (
        'code',
        'name',
        'price',
        'stock',
        'stock_applies'
    )

    list_display_links = (
        'code',
        'name',
    )

    # Search Configuration
    search_fields = (
        'code',
        'name'
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """"
    Admin Site Configuration for Order Model
    """

    # List page display configuration
    list_display = (
        'user',
        'total_price',
        'done',
        'last_change'
    )

    # Sidebar Filter Configuration
    list_filter = (
        'done',
    )

    # Order by not Done
    ordering = ('done', )