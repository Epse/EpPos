from django.urls import path
from django.conf.urls import url
from django.views.generic import RedirectView
from . import views
from . import apiviews

urlpatterns = [
    # Normal view URL's
    url(r'^$', RedirectView.as_view(pattern_name='order')),
    url(r'^addition/?$',
        views.addition, name='addition'),

    url(r'^order/add/(?P<product_id>[0-9A-Za-z_-]*/?$)',
        views.order_add_product, name='order_add_product'),
    url(r'^order/remove/(?P<product_id>[0-9]*)/?$',
        views.order_remove_product, name="order_remove_product"),
    url(r'^order/reset/?$', views.reset_order, name='reset_order'),
    url(r'^order/amount/?$', views.order_amount, name='order_get_amount'),
    url(r'^order/?$', views.order, name='order'),

    url(r'^pay/card/$', views.payment_card, name='payment_card'),
    url(r'^pay/cash/$', views.payment_cash, name='payment_cash'),

    url(r'^cash/(?P<amount>[0-9\.]*)/?$', views.cash, name='cash'),

    url(r'^view-order/(?P<order_id>[0-9]+)/?$', views.view_order,
        name='view_order'),
    url(r'^print-order/(?P<order_id>[0-9]+)/?$', views.print_order,
        name='print_order'),
    url(r'^print-current-order/?$', views.print_current_order,
        name='print_current_order'),

    url(r'^stock/?$', views.view_stock, name='view_stock'),

    # API URL's
    url(r'^api/orders/current/?$', apiviews.current_order,
        name='api_current_order'),
    path('api/orders/current/items/', apiviews.current_order_items,
         name='api_current_order_items')
]
