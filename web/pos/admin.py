from django.contrib import admin
from .models import Product, Cash, Order, Setting
from django.contrib.admin import SimpleListFilter
from django.db.models import F


admin.site.register(Cash)

# Disable the "Delete" action and batch action
admin.site.disable_action('delete_selected')

# Admin settings
admin.site.site_header = "EpPos Administration"
admin.site.site_title = "EpPos Administration"


# Admin Models
@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):

    # List Display Page Configuration
    list_display = (
        'key',
        'value'
    )


# Custom Filter for ProductAdmin
class LowStockFilter(SimpleListFilter):

    title = 'Stock Available'
    parameter_name = 'stock_available'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('low', 'Low Stock'),
            ('high', 'High Stock')
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value() == 'low':
            return queryset.filter(stock__lte=F('minimum_stock'))
        if self.value() == 'high':
            return queryset.filter(stock__gte=F('minimum_stock'))


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    The Admin Configuration for the model Product.
    """

    # Allow delete
    actions = ['delete_selected']

    # List Page Display Configuration
    list_display = (
        'name',
        'code',
        'price',
        'stock',
        'minimum_stock',
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

    # List filter
    list_filter = (
        LowStockFilter,
    )


# Safe deletion of orders
def safe_delete_order(modeladmin, request, queryset):
    queryset.filter(done=True).delete()
safe_delete_order.short_description = "Delete completed orders" #NOQA


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """"
    Admin Site Configuration for Order Model
    """

    # Add custom delete-if-not-done action
    actions = [safe_delete_order]

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
