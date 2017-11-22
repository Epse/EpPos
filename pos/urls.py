from django.conf.urls import url
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    url(r'^$', RedirectView.as_view(pattern_name='order')),
    url(r'^addition/?$',
        views.addition, name='addition'),
    url(r'^order/add/(?P<product_id>[0-9]*/?$)',
        views.order_add_product, name='order_add_product'),
    url(r'^order/remove/(?P<product_id>[0-9]*)/?$',
        views.order_remove_product, name="order_remove_product"),
    url(r'^order/reset/?$', views.reset_order, name='reset_order'),
    url(r'^order/?$', views.order, name='order'),
    url(r'^pay/card/$', views.payment_card, name='payment_card'),
    url(r'^pay/cash/$', views.payment_cash, name='payment_cash'),
    url(r'^cash/(?P<amount>[0-9\.]*)/?$', views.cash, name='cash')
]
